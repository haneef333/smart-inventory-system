import { useEffect, useState } from 'react'
import {
  getInventory,
  getRecipes,
  getProducts,
  addRecipeLine,
  deleteRecipeLine
} from '../api/client'
import Panel from '../components/Panel'
import { input, label, field, buttonPrimary, table, th, td } from '../components/ui'

export default function Recipes() {
  const [ingredients, setIngredients] = useState([])
  const [allRecipes, setAllRecipes] = useState([])
  const [products, setProducts] = useState([])
  const [selectedProduct, setSelectedProduct] = useState('')
  const [form, setForm] = useState({ product_name: '', ingredient_name: '', quantity_needed: '', unit: '' })
  const [notice, setNotice] = useState('')
async function handleDelete(id, productName, ingredientName) {
  try {
    await deleteRecipeLine(id)
    setNotice(`${ingredientName} removed from ${productName}.`)
    load()
  } catch (err) {
    setNotice('Failed to delete recipe line.')
  }
}
  const load = () => {
    getInventory().then(setIngredients)
    getRecipes().then(setAllRecipes)
    getProducts().then(list => {
      setProducts(list)
      setSelectedProduct(curr => curr || list[0] || '')
    })
  }

  useEffect(() => { load() }, [])

  useEffect(() => {
    if (ingredients.length && !form.ingredient_name) {
      setForm(f => ({ ...f, ingredient_name: ingredients[0].item_name }))
    }
  }, [ingredients])

  async function handleAdd(e) {
    e.preventDefault()
    if (!form.product_name || !form.ingredient_name || !form.quantity_needed) return
    await addRecipeLine({ ...form, quantity_needed: Number(form.quantity_needed) })
    setNotice(`Added ${form.ingredient_name} to ${form.product_name}.`)
    setForm(f => ({ ...f, quantity_needed: '', unit: '' }))
    load()
  }

  const productRows = allRecipes.filter(r => r.product_name === selectedProduct)

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 30 }}>Recipes</h1>
        <p style={{ color: 'var(--flour-dim)', marginTop: 6 }}>Bill of materials — ingredients per product</p>
      </div>

      {notice && (
        <div style={{ padding: '10px 14px', borderRadius: 8, marginBottom: 16, background: 'rgba(124,148,115,0.1)', border: '1px solid rgba(124,148,115,0.35)', color: 'var(--sage)', fontSize: 13 }}>
          {notice}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 20, alignItems: 'start' }}>
        <Panel title="Add recipe line">
          <form onSubmit={handleAdd}>
            <div style={field}>
              <label style={label}>Product name</label>
              <input
                style={input} placeholder="e.g. Bread, or a new product"
                list="product-suggestions"
                value={form.product_name}
                onChange={e => setForm(f => ({ ...f, product_name: e.target.value }))}
              />
              <datalist id="product-suggestions">
                {products.map(p => <option key={p} value={p} />)}
              </datalist>
            </div>
            <div style={field}>
              <label style={label}>Ingredient</label>
              <select
                style={input} value={form.ingredient_name}
                onChange={e => setForm(f => ({ ...f, ingredient_name: e.target.value }))}
              >
                {ingredients.map(i => <option key={i.id} value={i.item_name}>{i.item_name}</option>)}
              </select>
            </div>
            <div style={{ display: 'flex', gap: 10 }}>
              <div style={{ ...field, flex: 1 }}>
                <label style={label}>Quantity needed</label>
                <input type="number" step="any" min="0" style={input} value={form.quantity_needed}
                  onChange={e => setForm(f => ({ ...f, quantity_needed: e.target.value }))} />
              </div>
              <div style={{ ...field, flex: 1 }}>
                <label style={label}>Unit</label>
                <input style={input} placeholder="g, ml, pcs" value={form.unit}
                  onChange={e => setForm(f => ({ ...f, unit: e.target.value }))} />
              </div>
            </div>
            <button type="submit" style={{ ...buttonPrimary, width: '100%' }}>Add to recipe</button>
          </form>
        </Panel>

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          <Panel
            title="View recipe by product"
            action={
              <select
                style={{ ...input, width: 220 }}
                value={selectedProduct}
                onChange={e => setSelectedProduct(e.target.value)}
              >
                {products.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            }
          >
            {productRows.length === 0 ? (
              <div style={{ color: 'var(--flour-dim)', fontSize: 13 }}>No ingredients defined for this product yet.</div>
            ) : (
              <table style={table}>
                <thead>
                  <tr>{['Ingredient', 'Quantity needed', 'Unit'].map(h => <th key={h} style={th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {productRows.map((r, i) => (
                    <tr key={i}>
                      <td style={td}>{r.ingredient_name}</td>
                      <td style={td} className="num">{r.quantity_needed}</td>
                      <td style={{ ...td, color: 'var(--flour-dim)' }}>{r.unit}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </Panel>

          <Panel title={`All recipes (${allRecipes.length} lines)`}>
            <div style={{ maxHeight: 340, overflowY: 'auto' }}>
              <table style={table}>
                <thead>
                  <tr>
                    {['Product', 'Ingredient', 'Quantity', 'Unit', ''].map(h => (
                      <th key={h} style={th}>{h}</th>
                    ))}
                  </tr>               
                </thead>
                <tbody>
                  {allRecipes.map((r) => (
                    <tr key={r.id}>
                      <td style={td}>{r.product_name}</td>

                      <td style={{ ...td, color: 'var(--flour-dim)' }}>
                        {r.ingredient_name}
                      </td>

                      <td style={td} className="num">
                        {r.quantity_needed}
                      </td>

                      <td style={{ ...td, color: 'var(--flour-dim)' }}>
                        {r.unit}
                      </td>

                      <td style={td}>
                        <button
                          style={{
                            background: 'transparent',
                            border: '1px solid var(--jam)',
                            color: 'var(--jam)',
                            borderRadius: 6,
                            padding: '6px 10px',
                            cursor: 'pointer',
                            fontSize: 12
                          }}
                          onClick={() =>
                            handleDelete(r.id, r.product_name, r.ingredient_name)
                          }
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Panel>
        </div>
      </div>
    </div>
  )
}
