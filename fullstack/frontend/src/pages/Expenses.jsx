import { useEffect, useState } from 'react'
import { getExpenses, getExpenseCategories, addExpense, deleteExpense } from '../api/client'
import Panel from '../components/Panel'
import TicketCard from '../components/TicketCard'
import { input, label, field, buttonPrimary, buttonDanger, table, th, td, badge } from '../components/ui'

function money(n) {
  return `₹${Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
}

const CATEGORY_COLORS = {
  'Raw Material': '#c17a3d',
  'Packaging': '#e8c468',
  'Equipment & Tools': '#8f6fae',
  'Delivery & Logistics': '#4f8fa8',
  'Marketing': '#c1503a',
  'Utilities & Rent': '#7c9473',
  'Other': '#b8875a',
}

export default function Expenses() {
  const [expenses, setExpenses] = useState([])
  const [categories, setCategories] = useState([])
  const [form, setForm] = useState({ description: '', category: '', amount: '' })
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    getExpenses().then(setExpenses)
    getExpenseCategories().then(list => {
      setCategories(list)
      setForm(f => ({ ...f, category: f.category || list[0] || '' }))
    })
  }

  useEffect(() => { load() }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null)
    if (!form.description.trim()) { setError('Description is required.'); return }
    if (!form.amount || Number(form.amount) <= 0) { setError('Enter an amount greater than zero.'); return }

    setSubmitting(true)
    try {
      await addExpense({
        description: form.description.trim(),
        category: form.category,
        amount: Number(form.amount),
      })
      setForm(f => ({ ...f, description: '', amount: '' }))
      load()
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to add expense.')
    } finally {
      setSubmitting(false)
    }
  }

  async function handleDelete(id) {
    await deleteExpense(id)
    load()
  }

  const total = expenses.reduce((sum, e) => sum + e.amount, 0)
  const thisMonth = expenses.filter(e => {
    const d = new Date(e.expense_date)
    const now = new Date()
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
  }).reduce((sum, e) => sum + e.amount, 0)

  const rawMaterialTotal = expenses
    .filter(e => e.category === 'Raw Material')
    .reduce((sum, e) => sum + e.amount, 0)
  const packagingTotal = expenses
    .filter(e => e.category === 'Packaging')
    .reduce((sum, e) => sum + e.amount, 0)

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 30 }}>Expenses</h1>
        <p style={{ color: 'var(--flour-dim)', marginTop: 6 }}>Track ingredient, packaging, and running costs</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16, marginBottom: 16 }}>
        <TicketCard eyebrow="Total expenses" value={money(total)} accent="jam" />
        <TicketCard eyebrow="This month" value={money(thisMonth)} accent="amber" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 16, marginBottom: 20 }}>
        <TicketCard eyebrow="Raw material" value={money(rawMaterialTotal)} accent="sage" />
        <TicketCard eyebrow="Packaging" value={money(packagingTotal)} accent="butter" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 20, alignItems: 'start' }}>
        <Panel title="Log an expense">
          <form onSubmit={handleSubmit}>
            <div style={field}>
              <label style={label}>Description</label>
              <input
                type="text" style={input} placeholder="e.g. Flour, 25kg bag"
                value={form.description}
                onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              />
            </div>
            <div style={field}>
              <label style={label}>Category</label>
              <select
                style={input} value={form.category}
                onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
              >
                {categories.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>
            <div style={field}>
              <label style={label}>Amount</label>
              <input
                type="number" min="0" step="any" style={input} placeholder="0.00"
                value={form.amount}
                onChange={e => setForm(f => ({ ...f, amount: e.target.value }))}
              />
            </div>
            <button type="submit" disabled={submitting} style={{ ...buttonPrimary, width: '100%' }}>
              {submitting ? 'Saving…' : 'Add expense'}
            </button>
          </form>

          {error && (
            <div style={{ marginTop: 14, padding: 12, borderRadius: 8, background: 'rgba(193,80,58,0.1)', border: '1px solid rgba(193,80,58,0.35)' }}>
              <div style={{ color: 'var(--jam)', fontSize: 12 }}>{error}</div>
            </div>
          )}
        </Panel>

        <Panel title={`Expense log (${expenses.length})`}>
          <div style={{ maxHeight: 560, overflowY: 'auto' }}>
            <table style={table}>
              <thead>
                <tr>{['Description', 'Category', 'Amount', 'Date', ''].map(h => <th key={h} style={th}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {expenses.map(e => (
                  <tr key={e.id}>
                    <td style={td}>{e.description}</td>
                    <td style={td}>
                      <span style={badge(CATEGORY_COLORS[e.category] || '#b8875a')}>{e.category}</span>
                    </td>
                    <td style={td} className="num">{money(e.amount)}</td>
                    <td style={{ ...td, color: 'var(--flour-dim)' }}>{e.expense_date}</td>
                    <td style={td}>
                      <button style={buttonDanger} onClick={() => handleDelete(e.id)}>Delete</button>
                    </td>
                  </tr>
                ))}
                {expenses.length === 0 && (
                  <tr><td style={td} colSpan={5}>No expenses logged yet.</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  )
}
