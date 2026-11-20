import { useCallback, useEffect, useState } from 'react'
import {
  acceptOnlineOrder, declineOnlineOrder, getOnlineOrders, updateOnlineOrder,
} from '../api/client'
import {
  alertsEnabled, disableAlerts, enableAlerts, refreshOnlineOrderSummary, useOnlineOrderEvents, useOnlineOrderSummary,
} from '../hooks/useOnlineOrderSummary'
import { badge, buttonGhost, buttonPrimary, input } from '../components/ui'

const TABS = [
  { key: 'new', label: 'New' },
  { key: 'active', label: 'In progress' },
  { key: 'done', label: 'Done' },
]

const STATUS_COLORS = {
  new: '#e8c468', accepted: '#7c9473', baking: '#d99257', ready: '#7c9473',
  completed: '#c9c3b4', declined: '#c1503a', cancelled: '#c9c3b4',
}

const NEXT_STEP = {
  accepted: { status: 'baking', label: 'Start baking' },
  baking: { status: 'ready', label: 'Mark ready' },
  ready: { status: 'completed', label: 'Mark completed' },
}

const inr = n => `₹${Number(n || 0).toLocaleString('en-IN', { maximumFractionDigits: 2 })}`

// SQLite CURRENT_TIMESTAMP is UTC without a zone marker
const fromSqlite = ts => (ts ? new Date(ts.replace(' ', 'T') + 'Z') : null)
const timeAgo = ts => {
  const d = fromSqlite(ts)
  if (!d) return ''
  const mins = Math.round((Date.now() - d.getTime()) / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins} min ago`
  if (mins < 24 * 60) return `${Math.round(mins / 60)} h ago`
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })
}
const niceDate = iso => {
  if (!iso) return '—'
  const [y, m, d] = iso.split('-').map(Number)
  return new Date(y, m - 1, d).toLocaleDateString('en-IN', { weekday: 'short', day: 'numeric', month: 'short' })
}

export default function OnlineOrders() {
  const [tab, setTab] = useState('new')
  const [orders, setOrders] = useState(null)
  const [loadError, setLoadError] = useState(null)
  const summary = useOnlineOrderSummary()

  const load = useCallback(() => {
    return getOnlineOrders(tab)
      .then(list => { setOrders(list); setLoadError(null) })
      .catch(() => setLoadError('Could not load online orders. Is the backend running?'))
  }, [tab])

  useEffect(() => {
    setOrders(null)
    load()
    const t = setInterval(load, 15000)
    return () => clearInterval(t)
  }, [load])

  const afterChange = () => { load(); refreshOnlineOrderSummary() }

  // New orders and changes from other tabs show up instantly
  useOnlineOrderEvents(useCallback(() => { load() }, [load]))

  const [alertsOn, setAlertsOn] = useState(alertsEnabled)
  async function toggleAlerts() {
    if (alertsOn) { disableAlerts(); setAlertsOn(false) } else { await enableAlerts(); setAlertsOn(true) }
  }

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h1 style={{ fontSize: 30 }}>Online orders</h1>
        <p style={{ color: 'var(--flour-dim)', marginTop: 6 }}>
          Orders placed on the storefront. Accepting an order deducts its ingredients using your recipes.
        </p>
        <button
          type="button"
          onClick={toggleAlerts}
          style={{ ...buttonGhost, marginTop: 12, color: alertsOn ? 'var(--butter)' : 'var(--flour-dim)' }}
        >
          {alertsOn ? '🔔 Sound alerts on' : '🔕 Turn on sound alerts for new orders'}
        </button>
      </div>

      <div style={{ display: 'flex', gap: 8, marginBottom: 20, flexWrap: 'wrap' }}>
        {TABS.map(t => {
          const count = t.key === 'new' ? summary.new : t.key === 'active' ? summary.active : null
          const active = tab === t.key
          return (
            <button
              key={t.key}
              type="button"
              onClick={() => setTab(t.key)}
              style={{
                ...buttonGhost,
                background: active ? 'var(--panel)' : 'transparent',
                color: active ? 'var(--butter)' : 'var(--flour-dim)',
                borderColor: active ? 'rgba(232,196,104,0.45)' : 'var(--panel-border)',
              }}
            >
              {t.label}{count ? ` (${count})` : ''}
            </button>
          )
        })}
      </div>

      {loadError && <p style={{ color: 'var(--jam)' }}>{loadError}</p>}
      {!orders && !loadError && <p style={{ color: 'var(--flour-dim)' }}>Loading…</p>}
      {orders && orders.length === 0 && (
        <div style={emptyStyle}>
          {tab === 'new' && 'No new orders. New storefront orders appear here automatically.'}
          {tab === 'active' && 'Nothing in progress. Accepted orders show up here until they are completed.'}
          {tab === 'done' && 'Completed, declined and cancelled orders will be listed here.'}
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: 16, alignItems: 'start' }}>
        {orders?.map(o => <OrderCard key={o.id} order={o} onChange={afterChange} />)}
      </div>
    </div>
  )
}

function OrderCard({ order, onChange }) {
  const [busy, setBusy] = useState(false)
  const [errors, setErrors] = useState(null)
  const [result, setResult] = useState(null)
  const [declining, setDeclining] = useState(false)
  const [reason, setReason] = useState('')

  async function run(action) {
    setBusy(true); setErrors(null)
    try {
      const res = await action()
      return res
    } catch (err) {
      const detail = err?.response?.data?.detail
      setErrors(Array.isArray(detail) ? detail : [typeof detail === 'string' ? detail : 'Something went wrong. Try again.'])
      return null
    } finally {
      setBusy(false)
    }
  }

  async function accept() {
    const res = await run(() => acceptOnlineOrder(order.id))
    if (res) { setResult(res); setTimeout(onChange, 2500) }
  }

  async function decline() {
    const res = await run(() => declineOnlineOrder(order.id, reason))
    if (res) onChange()
  }

  async function advance(update) {
    const res = await run(() => updateOnlineOrder(order.id, update))
    if (res) onChange()
  }

  const next = NEXT_STEP[order.status]
  const stock = order.stock_check

  return (
    <section style={cardStyle}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 10, alignItems: 'flex-start' }}>
        <div>
          <div style={{ fontWeight: 600, fontSize: 16 }}>{order.customer_name}</div>
          <div style={{ color: 'var(--flour-dim)', fontSize: 12, fontFamily: 'var(--font-mono)', marginTop: 2 }}>
            {order.external_id} · {timeAgo(order.received_at)}
          </div>
        </div>
        <span style={badge(STATUS_COLORS[order.status] || '#c9c3b4')}>{order.status}</span>
      </div>

      <dl style={metaGrid}>
        <dt style={dtStyle}>Needed by</dt>
        <dd style={ddStyle}>{niceDate(order.due_date)}{order.time_slot ? `, ${order.time_slot.toLowerCase()}` : ''}</dd>
        <dt style={dtStyle}>{order.fulfilment === 'delivery' ? 'Deliver to' : 'Pickup'}</dt>
        <dd style={ddStyle}>{order.fulfilment === 'delivery' ? order.address : 'Customer collects'}</dd>
        <dt style={dtStyle}>Phone</dt>
        <dd style={ddStyle}><a href={`tel:${order.customer_phone}`} style={{ color: 'var(--butter)' }}>{order.customer_phone}</a></dd>
        <dt style={dtStyle}>Payment</dt>
        <dd style={ddStyle}>{order.payment_method === 'online' ? 'UPI' : 'Cash'}, {order.payment_status}</dd>
      </dl>

      <ul style={{ listStyle: 'none', padding: 0, margin: '12px 0', fontSize: 14 }}>
        {order.items.map((i, idx) => (
          <li key={idx} style={{ display: 'flex', justifyContent: 'space-between', gap: 10, padding: '6px 0', borderBottom: '1px dashed var(--panel-border)' }}>
            <span style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <span>{i.quantity} × {i.display_name || i.product_name}</span>
              <span style={{ color: 'var(--flour-dim)', fontSize: 12 }}>
                Recipe: {i.product_name}{i.recipe_scale && i.recipe_scale !== 1 ? ` × ${i.recipe_scale}` : ''}
              </span>
              {i.details && <span style={{ color: 'var(--butter)', fontSize: 13 }}>{i.details}</span>}
              {i.photo_url && (
                <a href={i.photo_url} target="_blank" rel="noreferrer" style={{ display: 'inline-flex', alignItems: 'center', gap: 8, color: 'var(--flour-dim)', fontSize: 12 }}>
                  <img src={i.photo_url} alt="Customer's reference design" style={{ width: 56, height: 56, objectFit: 'cover', borderRadius: 8, border: '1px solid var(--panel-border)' }} />
                  Reference photo (opens full size)
                </a>
              )}
            </span>
            <span className="num" style={{ whiteSpace: 'nowrap' }}>{inr(i.unit_price * i.quantity)}</span>
          </li>
        ))}
        {order.discount > 0 && (
          <li style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', color: 'var(--flour-dim)' }}>
            <span>Coupon {order.coupon_code}</span><span className="num">−{inr(order.discount)}</span>
          </li>
        )}
        {order.delivery_fee > 0 && (
          <li style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', color: 'var(--flour-dim)' }}>
            <span>Delivery</span><span className="num">{inr(order.delivery_fee)}</span>
          </li>
        )}
        <li style={{ display: 'flex', justifyContent: 'space-between', padding: '8px 0 0', fontWeight: 600 }}>
          <span>Total</span><span className="num">{inr(order.total)}</span>
        </li>
      </ul>

      {order.notes && (
        <div style={notesStyle}>
          <span style={{ color: 'var(--flour-dim)', fontSize: 12 }}>Customer note</span>
          <div>{order.notes}</div>
        </div>
      )}

      {order.status === 'declined' && order.status_note && (
        <p style={{ color: 'var(--flour-dim)', fontSize: 13 }}>Declined: {order.status_note}</p>
      )}
      {order.status === 'cancelled' && (
        <p style={{ color: 'var(--flour-dim)', fontSize: 13 }}>The customer cancelled this order before it was accepted.</p>
      )}

      {/* New: stock check, then accept or decline */}
      {order.status === 'new' && !result && (
        <>
          {stock && (
            <div style={stock.can_fulfil ? okBox : warnBox}>
              {stock.can_fulfil
                ? 'Enough stock for this order.'
                : <>
                    <div style={{ fontWeight: 600, marginBottom: 4 }}>Not enough stock right now</div>
                    {stock.shortages.map((s, i) => <div key={i}>{s}</div>)}
                    <div style={{ marginTop: 6, color: 'var(--flour-dim)' }}>Restock on the Inventory page, then accept, or decline the order.</div>
                  </>}
            </div>
          )}

          {!declining ? (
            <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
              <button type="button" style={{ ...buttonPrimary, flex: 1, opacity: busy ? 0.6 : 1 }} disabled={busy} onClick={accept}>
                {busy ? 'Accepting…' : 'Accept and deduct stock'}
              </button>
              <button type="button" style={buttonGhost} disabled={busy} onClick={() => setDeclining(true)}>Decline</button>
            </div>
          ) : (
            <div style={{ marginTop: 12 }}>
              <label style={{ fontSize: 12, color: 'var(--flour-dim)', display: 'block', marginBottom: 6 }}>
                Reason (the customer will see this)
              </label>
              <textarea
                rows={2}
                style={{ ...input, resize: 'vertical' }}
                value={reason}
                onChange={e => setReason(e.target.value)}
                placeholder="e.g. Fully booked on that date"
              />
              <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
                <button type="button" style={{ ...buttonPrimary, background: 'var(--jam)', color: 'var(--flour)' }} disabled={busy} onClick={decline}>
                  {busy ? 'Declining…' : 'Decline order'}
                </button>
                <button type="button" style={buttonGhost} disabled={busy} onClick={() => setDeclining(false)}>Back</button>
              </div>
            </div>
          )}
        </>
      )}

      {result && (
        <div style={okBox}>
          <div style={{ fontWeight: 600, marginBottom: 4 }}>Accepted. The customer has been notified.</div>
          <div>Stock deducted: {Object.entries(result.deducted).map(([k, v]) => `${k} ${v}`).join(', ')}</div>
          <div style={{ marginTop: 4 }}>Revenue {inr(result.revenue)}, cost {inr(result.total_cost)}, profit {inr(result.profit)}</div>
        </div>
      )}

      {/* In progress: move it along */}
      {next && (
        <div style={{ display: 'flex', gap: 8, marginTop: 12, flexWrap: 'wrap' }}>
          <button type="button" style={{ ...buttonPrimary, flex: 1, opacity: busy ? 0.6 : 1 }} disabled={busy} onClick={() => advance({ status: next.status })}>
            {next.label}
          </button>
          <button
            type="button"
            style={buttonGhost}
            disabled={busy}
            onClick={() => advance({ payment_status: order.payment_status === 'paid' ? 'unpaid' : 'paid' })}
          >
            {order.payment_status === 'paid' ? 'Mark unpaid' : 'Mark paid'}
          </button>
        </div>
      )}

      {errors && (
        <div style={{ ...warnBox, marginTop: 12 }}>
          {errors.map((e, i) => <div key={i}>{e}</div>)}
        </div>
      )}

      {order.callback_state === 'failed' && (
        <p style={{ color: 'var(--flour-dim)', fontSize: 12, marginTop: 10 }}>
          The storefront could not be reached, so the customer hasn’t seen the latest status yet. It will retry automatically.
        </p>
      )}
    </section>
  )
}

const cardStyle = {
  background: 'var(--panel)',
  border: '1px solid var(--panel-border)',
  borderRadius: 14,
  padding: 18,
}
const metaGrid = {
  display: 'grid',
  gridTemplateColumns: 'auto 1fr',
  gap: '6px 14px',
  margin: '14px 0 0',
  fontSize: 13,
}
const dtStyle = { color: 'var(--flour-dim)' }
const ddStyle = { margin: 0 }
const notesStyle = {
  padding: '10px 12px',
  borderRadius: 8,
  background: 'var(--charcoal-soft)',
  border: '1px solid var(--panel-border)',
  fontSize: 14,
  marginBottom: 4,
}
const okBox = {
  marginTop: 12,
  padding: '10px 12px',
  borderRadius: 8,
  fontSize: 13,
  background: 'rgba(124,148,115,0.12)',
  border: '1px solid rgba(124,148,115,0.4)',
  color: '#b9cdb1',
}
const warnBox = {
  marginTop: 12,
  padding: '10px 12px',
  borderRadius: 8,
  fontSize: 13,
  background: 'rgba(193,80,58,0.1)',
  border: '1px solid rgba(193,80,58,0.35)',
  color: '#e59a8a',
}
const emptyStyle = {
  padding: 24,
  borderRadius: 14,
  border: '1px dashed var(--panel-border)',
  color: 'var(--flour-dim)',
  fontSize: 14,
}
