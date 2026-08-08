import { useEffect, useState } from 'react'
import { getInventory, addInventoryItem, restockItem, deleteInventoryItem } from '../api/client'
import Panel from '../components/Panel'
import { input, label, field, buttonPrimary, buttonDanger, table, th, td, badge } from '../components/ui'

const emptyForm = { item_name: '', category: '', quantity: 0, unit: '', cost_per_unit: 0, reorder_threshold: 10 }

export default function Inventory() {
  const [items, setItems] = useState([])
  const [form, setForm] = useState(emptyForm)
  const [restockQty, setRestockQty] = useState({})
  const [error, setError] = useState('')
  const [notice, setNotice] = useState('')

  const load = () => getInventory().then(setItems)

  useEffect(() => { load() }, [])

  async function handleAdd(e) {
    e.preventDefault()
    setError(''); setNotice('')
    try {
      await addInventoryItem({
        ...form,
        quantity: Number(form.quantity),
        cost_per_unit: Number(form.cost_per_unit),
        reorder_threshold: Number(form.reorder_threshold),
      })
      setForm(emptyForm)
      setNotice(`${form.item_name} added.`)
      load()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to add item.')
    }
  }

  async function handleRestock(id, name) {
    const qty = Number(restockQty[id] || 0)
    if (!qty) return
    await restockItem(id, qty)
    setRestockQty(r => ({ ...r, [id]: '' }))
    setNotice(`${name} restocked by ${qty}.`)
    load()
  }

  async function handleDelete(id, name) {
    await deleteInventoryItem(id)
    setNotice(`${name} deleted.`)
    load()
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 30 }}>Inventory</h1>
        <p style={{ color: 'var(--flour-dim)', marginTop: 6 }}>Ingredients, stock levels, and reorder thresholds</p>
      </div>

      {notice && <Banner text={notice} color="var(--sage)" />}
      {error && <Banner text={error} color="var(--jam)" />}

      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 20, alignItems: 'start' }}>
        <Panel title="Add new item">
          <form onSubmit={handleAdd}>
            <div style={field}>
              <label style={label}>Item name</label>
              <input style={input} required value={form.item_name}
                onChange={e => setForm(f => ({ ...f, item_name: e.target.value }))} />
            </div>
            <div style={field}>
              <label style={label}>Category</label>
              <input style={input} value={form.category}
                onChange={e => setForm(f => ({ ...f, category: e.target.value }))} />
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <div style={{ ...field, flex: 1 }}>
                <label style={label}>Quantity</label>
                <input type="number" step="any" min="0" style={input} value={form.quantity}
                  onChange={e => setForm(f => ({ ...f, quantity: e.target.value }))} />
              </div>
              <div style={{ ...field, flex: 1 }}>
                <label style={label}>Unit</label>
                <input style={input} placeholder="g, ml, pcs" value={form.unit}
                  onChange={e => setForm(f => ({ ...f, unit: e.target.value }))} />
              </div>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <div style={{ ...field, flex: 1 }}>
                <label style={label}>Cost per unit</label>
                <input type="number" step="any" min="0" style={input} value={form.cost_per_unit}
                  onChange={e => setForm(f => ({ ...f, cost_per_unit: e.target.value }))} />
              </div>
              <div style={{ ...field, flex: 1 }}>
                <label style={label}>Reorder threshold</label>
                <input type="number" step="any" min="0" style={input} value={form.reorder_threshold}
                  onChange={e => setForm(f => ({ ...f, reorder_threshold: e.target.value }))} />
              </div>
            </div>
            <button type="submit" style={{ ...buttonPrimary, width: '100%', marginTop: 6 }}>Add item</button>
          </form>
        </Panel>

        <Panel title={`Current stock (${items.length})`}>
          <div style={{ overflowX: 'auto' }}>
            <table style={table}>
              <thead>
                <tr>
                  {['Item', 'Category', 'Qty', 'Cost/unit', 'Status', 'Restock', ''].map(h => (
                    <th key={h} style={th}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {items.map(it => {
                  const low = it.quantity <= it.reorder_threshold
                  return (
                    <tr key={it.id}>
                      <td style={td}>{it.item_name}</td>
                      <td style={{ ...td, color: 'var(--flour-dim)' }}>{it.category}</td>
                      <td style={{ ...td }} className="num">{it.quantity} {it.unit}</td>
                      <td style={td} className="num">₹{it.cost_per_unit}</td>
                      <td style={td}>
                        <span style={badge(low ? 'var(--jam)' : 'var(--sage)')}>
                          {low ? 'Low stock' : 'OK'}
                        </span>
                      </td>
                      <td style={td}>
                        <div style={{ display: 'flex', gap: 6 }}>
                          <input
                            type="number" min="0" placeholder="qty"
                            style={{ ...input, width: 70, padding: '6px 8px' }}
                            value={restockQty[it.id] || ''}
                            onChange={e => setRestockQty(r => ({ ...r, [it.id]: e.target.value }))}
                          />
                          <button
                            style={{ ...buttonPrimary, padding: '6px 10px', fontSize: 12 }}
                            onClick={() => handleRestock(it.id, it.item_name)}
                          >
                            Add
                          </button>
                        </div>
                      </td>
                      <td style={td}>
                        <button style={buttonDanger} onClick={() => handleDelete(it.id, it.item_name)}>Delete</button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  )
}

function Banner({ text, color }) {
  return (
    <div style={{
      padding: '10px 14px', borderRadius: 8, marginBottom: 16,
      background: `${color}18`, border: `1px solid ${color}55`, color, fontSize: 13,
    }}>
      {text}
    </div>
  )
}
