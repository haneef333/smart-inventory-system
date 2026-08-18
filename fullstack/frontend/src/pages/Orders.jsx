import { useEffect, useState } from 'react'
import { getProducts, getOrders, placeOrder, updateOrderStatus } from '../api/client'
import Panel from '../components/Panel'
import TicketCard from '../components/TicketCard'
import { input, label, field, buttonPrimary, table, th, td, badge } from '../components/ui'

const DELIVERY_COLORS = { pending: '#e8c468', delivered: '#7c9473', cancelled: '#c1503a' }
const PAYMENT_COLORS = { unpaid: '#c1503a', paid: '#7c9473' }

export default function Orders() {
  const [products, setProducts] = useState([])
  const [orders, setOrders] = useState([])
  const [form, setForm] = useState({
    product_name: '', order_quantity: 1, selling_price: 0,
    customer_name: '', due_date: '', payment_method: 'cash',
  })
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [submitting, setSubmitting] = useState(false)

  const load = () => {
    getProducts().then(list => {
      setProducts(list)
      setForm(f => ({ ...f, product_name: f.product_name || list[0] || '' }))
    })
    getOrders().then(setOrders)
  }

  useEffect(() => { load() }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setError(null); setResult(null); setSubmitting(true)
    try {
      const res = await placeOrder({
        ...form,
        order_quantity: Number(form.order_quantity),
        selling_price: Number(form.selling_price),
        customer_name: form.customer_name || null,
        due_date: form.due_date || null,
      })
      setResult(res)
      load()
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(Array.isArray(detail) ? detail : [detail || 'Order failed.'])
    } finally {
      setSubmitting(false)
    }
  }

  async function cycleDeliveryStatus(o) {
    const next = o.delivery_status === 'pending' ? 'delivered'
      : o.delivery_status === 'delivered' ? 'cancelled' : 'pending'
    await updateOrderStatus(o.id, { delivery_status: next })
    load()
  }

  async function togglePaymentStatus(o) {
    const next = o.payment_status === 'unpaid' ? 'paid' : 'unpaid'
    await updateOrderStatus(o.id, { payment_status: next })
    load()
  }

  const cashTotal = orders
    .filter(o => (o.payment_method || 'cash') === 'cash')
    .reduce((sum, o) => sum + o.selling_price * o.quantity, 0)
  const onlineTotal = orders
    .filter(o => o.payment_method === 'online')
    .reduce((sum, o) => sum + o.selling_price * o.quantity, 0)
  const pendingCount = orders.filter(o => (o.delivery_status || 'pending') === 'pending').length
  const completedCount = orders.filter(o => o.delivery_status === 'delivered').length

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 30 }}>Orders</h1>
        <p style={{ color: 'var(--flour-dim)', marginTop: 6 }}>Place an order — stock is checked and deducted automatically</p>
      </div>

      <div style={{ marginBottom: 16 }}>
        <TicketCard eyebrow="Total orders amount" value={`₹${(cashTotal + onlineTotal).toFixed(0)}`} accent="amber" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 20 }}>
        <TicketCard eyebrow="Cash" value={`₹${cashTotal.toFixed(0)}`} accent="sage" />
        <TicketCard eyebrow="Online" value={`₹${onlineTotal.toFixed(0)}`} accent="butter" />
        <TicketCard eyebrow="Pending orders" value={pendingCount} accent="jam" />
        <TicketCard eyebrow="Completed orders" value={completedCount} accent="sage" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '340px 1fr', gap: 20, alignItems: 'start' }}>
        <Panel title="Place order">
          <form onSubmit={handleSubmit}>
            <div style={field}>
              <label style={label}>Product</label>
              <select
                style={input} value={form.product_name}
                onChange={e => setForm(f => ({ ...f, product_name: e.target.value }))}
              >
                {products.map(p => <option key={p} value={p}>{p}</option>)}
              </select>
            </div>
            <div style={field}>
              <label style={label}>Quantity ordered</label>
              <input type="number" min="1" step="1" style={input} value={form.order_quantity}
                onChange={e => setForm(f => ({ ...f, order_quantity: e.target.value }))} />
            </div>
            <div style={field}>
              <label style={label}>Selling price (per unit)</label>
              <input type="number" min="0" step="any" style={input} value={form.selling_price}
                onChange={e => setForm(f => ({ ...f, selling_price: e.target.value }))} />
            </div>
            <div style={field}>
              <label style={label}>Customer name (optional)</label>
              <input type="text" style={input} value={form.customer_name}
                onChange={e => setForm(f => ({ ...f, customer_name: e.target.value }))} />
            </div>
            <div style={field}>
              <label style={label}>Due date (optional)</label>
              <input type="date" style={input} value={form.due_date}
                onChange={e => setForm(f => ({ ...f, due_date: e.target.value }))} />
            </div>
            <div style={field}>
              <label style={label}>Payment method</label>
              <select
                style={input} value={form.payment_method}
                onChange={e => setForm(f => ({ ...f, payment_method: e.target.value }))}
              >
                <option value="cash">Cash</option>
                <option value="online">Online</option>
              </select>
            </div>
            <button type="submit" disabled={submitting} style={{ ...buttonPrimary, width: '100%' }}>
              {submitting ? 'Processing…' : 'Place order'}
            </button>
          </form>

          {error && (
            <div style={{ marginTop: 14, padding: 12, borderRadius: 8, background: 'rgba(193,80,58,0.1)', border: '1px solid rgba(193,80,58,0.35)' }}>
              {error.map((e, i) => (
                <div key={i} style={{ color: 'var(--jam)', fontSize: 12, marginBottom: 4 }}>{e}</div>
              ))}
            </div>
          )}

          {result && (
            <div style={{ marginTop: 16, display: 'grid', gap: 10 }}>
              <TicketCard eyebrow="Order processed" value={`✓ ${result.product_name}`} accent="sage" />
              <div style={{ fontSize: 13, display: 'grid', gap: 6 }}>
                <Row label="Total cost" value={`₹${result.total_cost.toFixed(2)}`} />
                <Row label="Revenue" value={`₹${result.revenue.toFixed(2)}`} />
                <Row label="Profit" value={`₹${result.profit.toFixed(2)}`} accent />
              </div>
            </div>
          )}
        </Panel>

        <Panel title={`Order history (${orders.length})`}>
          <div style={{ maxHeight: 560, overflowY: 'auto' }}>
            <table style={table}>
              <thead>
                <tr>{['Product', 'Qty', 'Price', 'Customer', 'Due', 'Method', 'Delivery', 'Payment', 'Date'].map(h => <th key={h} style={th}>{h}</th>)}</tr>
              </thead>
              <tbody>
                {orders.map(o => (
                  <tr key={o.id}>
                    <td style={td}>{o.product_name}</td>
                    <td style={td} className="num">{o.quantity}</td>
                    <td style={td} className="num">₹{o.selling_price}</td>
                    <td style={{ ...td, color: 'var(--flour-dim)' }}>{o.customer_name || '—'}</td>
                    <td style={{ ...td, color: 'var(--flour-dim)' }}>{o.due_date || '—'}</td>
                    <td style={td}>
                      <span style={badge(o.payment_method === 'online' ? '#4f8fa8' : '#7c9473')}>
                        {o.payment_method || 'cash'}
                      </span>
                    </td>
                    <td style={td}>
                      <span
                        style={{ ...badge(DELIVERY_COLORS[o.delivery_status] || '#e8c468'), cursor: 'pointer' }}
                        title="Click to change"
                        onClick={() => cycleDeliveryStatus(o)}
                      >
                        {o.delivery_status}
                      </span>
                    </td>
                    <td style={td}>
                      <span
                        style={{ ...badge(PAYMENT_COLORS[o.payment_status] || '#c1503a'), cursor: 'pointer' }}
                        title="Click to change"
                        onClick={() => togglePaymentStatus(o)}
                      >
                        {o.payment_status}
                      </span>
                    </td>
                    <td style={{ ...td, color: 'var(--flour-dim)' }}>{o.order_date}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>
      </div>
    </div>
  )
}

function Row({ label, value, accent }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
      <span style={{ color: 'var(--flour-dim)' }}>{label}</span>
      <span className="num" style={{ color: accent ? 'var(--sage)' : 'var(--flour)' }}>{value}</span>
    </div>
  )
}
