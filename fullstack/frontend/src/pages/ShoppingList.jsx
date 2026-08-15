import { useEffect, useState } from 'react'
import { getProducts, generateShoppingList } from '../api/client'
import Panel from '../components/Panel'
import TicketCard from '../components/TicketCard'
import { input, label, field, buttonPrimary, buttonGhost, buttonDanger, table, th, td } from '../components/ui'

function money(n) {
  return `₹${Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
}

export default function ShoppingList() {
  const [products, setProducts] = useState([])
  const [planned, setPlanned] = useState([])
  const [draft, setDraft] = useState({ product_name: '', quantity: 1 })
  const [includeLowStock, setIncludeLowStock] = useState(true)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    getProducts().then(list => {
      setProducts(list)
      setDraft(d => ({ ...d, product_name: d.product_name || list[0] || '' }))
    })
  }, [])

  function addPlannedItem() {
    if (!draft.product_name || Number(draft.quantity) <= 0) return
    setPlanned(p => [...p, { product_name: draft.product_name, quantity: Number(draft.quantity) }])
  }

  function removePlannedItem(i) {
    setPlanned(p => p.filter((_, idx) => idx !== i))
  }

  async function handleGenerate() {
    setLoading(true)
    try {
      const res = await generateShoppingList({ items: planned, include_low_stock: includeLowStock })
      setResult(res)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 30 }}>Shopping list</h1>
        <p style={{ color: 'var(--flour-dim)', marginTop: 6 }}>
          Add the batches you're planning to bake — we'll work out what to buy
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 20, alignItems: 'start' }}>
        <Panel title="Planned batches">
          <div style={field}>
            <label style={label}>Product</label>
            <select
              style={input} value={draft.product_name}
              onChange={e => setDraft(d => ({ ...d, product_name: e.target.value }))}
            >
              {products.map(p => <option key={p} value={p}>{p}</option>)}
            </select>
          </div>
          <div style={field}>
            <label style={label}>Quantity</label>
            <input
              type="number" min="1" step="1" style={input} value={draft.quantity}
              onChange={e => setDraft(d => ({ ...d, quantity: e.target.value }))}
            />
          </div>
          <button type="button" style={{ ...buttonGhost, width: '100%', marginBottom: 16 }} onClick={addPlannedItem}>
            + Add to plan
          </button>

          {planned.length > 0 && (
            <div style={{ display: 'grid', gap: 8, marginBottom: 16 }}>
              {planned.map((p, i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: 13 }}>
                  <span>{p.quantity}× {p.product_name}</span>
                  <button style={buttonDanger} onClick={() => removePlannedItem(i)}>Remove</button>
                </div>
              ))}
            </div>
          )}

          <div style={{ ...field, display: 'flex', alignItems: 'center', gap: 8 }}>
            <input
              type="checkbox" id="lowstock" checked={includeLowStock}
              onChange={e => setIncludeLowStock(e.target.checked)}
            />
            <label htmlFor="lowstock" style={{ fontSize: 13, color: 'var(--flour-dim)' }}>
              Also include items already running low
            </label>
          </div>

          <button
            type="button" disabled={loading || (planned.length === 0 && !includeLowStock)}
            style={{ ...buttonPrimary, width: '100%' }}
            onClick={handleGenerate}
          >
            {loading ? 'Generating…' : 'Generate shopping list'}
          </button>
        </Panel>

        <Panel title={result ? `Shopping list (${result.items.length} items)` : 'Shopping list'}>
          {!result && (
            <div style={{ color: 'var(--flour-dim)', fontSize: 13 }}>
              Add planned batches (or just tick "include low stock") and generate your list.
            </div>
          )}

          {result && (
            <>
              <div style={{ marginBottom: 16 }}>
                <TicketCard eyebrow="Estimated total cost" value={money(result.total_estimated_cost)} accent="amber" />
              </div>

              {result.unresolved_products.length > 0 && (
                <div style={{ marginBottom: 14, padding: 12, borderRadius: 8, background: 'rgba(193,80,58,0.1)', border: '1px solid rgba(193,80,58,0.35)' }}>
                  <div style={{ color: 'var(--jam)', fontSize: 12 }}>
                    No recipe found for: {result.unresolved_products.join(', ')}
                  </div>
                </div>
              )}

              <div style={{ maxHeight: 480, overflowY: 'auto' }}>
                <table style={table}>
                  <thead>
                    <tr>{['Item', 'Category', 'Need to buy', 'In stock', 'Est. cost', 'Why'].map(h => <th key={h} style={th}>{h}</th>)}</tr>
                  </thead>
                  <tbody>
                    {result.items.map((it, i) => (
                      <tr key={i}>
                        <td style={td}>{it.item_name}</td>
                        <td style={{ ...td, color: 'var(--flour-dim)' }}>{it.category}</td>
                        <td style={td} className="num">{it.purchase_qty} {it.unit || ''}</td>
                        <td style={td} className="num">{it.currently_in_stock} {it.unit || ''}</td>
                        <td style={td} className="num">{money(it.estimated_cost)}</td>
                        <td style={{ ...td, color: 'var(--flour-dim)', fontSize: 12 }}>{it.reason}</td>
                      </tr>
                    ))}
                    {result.items.length === 0 && (
                      <tr><td style={td} colSpan={6}>Nothing to buy — you're fully stocked.</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </Panel>
      </div>
    </div>
  )
}
