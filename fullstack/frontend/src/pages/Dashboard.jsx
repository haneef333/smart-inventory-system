import { useEffect, useState } from 'react'
import {
  AreaChart, Area, BarChart, Bar, LineChart, Line, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'
import { getDashboardMeta, getDashboardSummary, getOrders, getExpenses } from '../api/client'
import TicketCard from '../components/TicketCard'
import Panel from '../components/Panel'
import TaskCalendar from '../components/TaskCalendar'
import { input, label, field } from '../components/ui'

const PIE_COLORS = ['#c17a3d', '#7c9473', '#c1503a', '#e8c468', '#8f6fae', '#4f8fa8', '#b8875a', '#5c8f6d']

function money(n) {
  return `₹${Number(n).toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
}

export default function Dashboard() {
  const [meta, setMeta] = useState(null)
  const [filters, setFilters] = useState({ start_date: '', end_date: '', product: 'All' })
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [recentOrders, setRecentOrders] = useState([])
  const [recentExpenses, setRecentExpenses] = useState([])

  useEffect(() => {
    getOrders().then(rows => setRecentOrders(rows.slice(0, 5)))
    getExpenses().then(rows => setRecentExpenses(rows.slice(0, 5)))
  }, [])

  useEffect(() => {
    getDashboardMeta().then(m => {
      setMeta(m)
      setFilters({
        start_date: m.min_date || '',
        end_date: m.max_date || '',
        product: 'All',
      })
    })
  }, [])

  useEffect(() => {
    if (!filters.start_date || !filters.end_date) return
    setLoading(true)
    getDashboardSummary(filters).then(d => {
      setSummary(d)
      setLoading(false)
    })
  }, [filters])

  if (!meta) return <div className="eyebrow">Loading dashboard…</div>

  return (
    <div>
      <PageHeader title="Dashboard" subtitle="Revenue, profit, and stock at a glance" />

      {!loading && summary && !summary.empty && (
        <div className="kpi-row">
          <TicketCard eyebrow="Total profit" value={money(summary.kpis.total_profit)} accent="sage" />
          <TicketCard eyebrow="Completed sales" value={summary.kpis.total_orders} accent="butter" />
          <TicketCard eyebrow="Total sales" value={money(summary.kpis.total_revenue)} accent="amber" />
          <TicketCard eyebrow="Total expenses" value={money(summary.kpis.total_expenses)} accent="jam" />
        </div>
      )}

      <div style={{ marginBottom: 20 }}>
        <TaskCalendar />
      </div>

      <div className="two-col">
        <Panel title="Recent orders">
          <RecentOrdersList rows={recentOrders} />
        </Panel>
        <Panel title="Recent expenses">
          <RecentExpensesList rows={recentExpenses} />
        </Panel>
      </div>

      <div style={styles.filterRow}>
        <div style={{ ...field, width: 160, marginBottom: 0 }}>
          <label style={label}>From</label>
          <input
            type="date" style={input} value={filters.start_date}
            min={meta.min_date} max={meta.max_date}
            onChange={e => setFilters(f => ({ ...f, start_date: e.target.value }))}
          />
        </div>
        <div style={{ ...field, width: 160, marginBottom: 0 }}>
          <label style={label}>To</label>
          <input
            type="date" style={input} value={filters.end_date}
            min={meta.min_date} max={meta.max_date}
            onChange={e => setFilters(f => ({ ...f, end_date: e.target.value }))}
          />
        </div>
        <div style={{ ...field, width: 220, marginBottom: 0 }}>
          <label style={label}>Product</label>
          <select
            style={input} value={filters.product}
            onChange={e => setFilters(f => ({ ...f, product: e.target.value }))}
          >
            <option value="All">All products</option>
            {meta.products.map(p => <option key={p} value={p}>{p}</option>)}
          </select>
        </div>
      </div>

      {loading && <div className="eyebrow">Loading…</div>}

      {!loading && summary?.empty && (
        <Panel><div>No sales data for this selection.</div></Panel>
      )}

      {!loading && summary && !summary.empty && (
        <>
          <div className="two-col">
            <Panel title="Highlights">
              <SummaryLine label="Total orders" value={summary.kpis.total_orders} />
              <SummaryLine label="Net profit" value={money(summary.kpis.net_profit)} />
              <SummaryLine label="Highest revenue product" value={summary.executive_summary.highest_revenue_product} />
              <SummaryLine label="Highest profit product" value={summary.executive_summary.highest_profit_product} />
              <SummaryLine label="Average order value" value={money(summary.executive_summary.average_order_value)} last />
            </Panel>

            <Panel title="Inventory overview">
              <SummaryLine label="Products in inventory" value={summary.inventory_overview.products_in_inventory} />
              <SummaryLine label="Total stock" value={summary.inventory_overview.total_stock} />
              <SummaryLine
                label="Low stock items"
                value={summary.inventory_overview.low_stock_count}
                warn={summary.inventory_overview.low_stock_count > 0}
                last
              />
            </Panel>
          </div>

          <Panel title="Revenue trend">
            <ResponsiveContainer width="100%" height={280}>
              <AreaChart data={summary.charts.daily_revenue}>
                <defs>
                  <linearGradient id="revFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#c17a3d" stopOpacity={0.5} />
                    <stop offset="100%" stopColor="#c17a3d" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--panel-border)" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} minTickGap={50} />
                <YAxis tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Area type="monotone" dataKey="revenue" stroke="#c17a3d" fill="url(#revFill)" strokeWidth={2} />
              </AreaChart>
            </ResponsiveContainer>
          </Panel>

          <div className="two-col">
            <Panel title="Monthly revenue">
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={summary.charts.monthly_revenue}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--panel-border)" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                  <YAxis tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="revenue" fill="#c17a3d" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Panel>

            <Panel title="Monthly profit">
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={summary.charts.monthly_profit}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--panel-border)" />
                  <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                  <YAxis tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="profit" fill="#7c9473" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Panel>
          </div>

          <Panel title="Profit trend">
            <ResponsiveContainer width="100%" height={240}>
              <LineChart data={summary.charts.daily_profit}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--panel-border)" />
                <XAxis dataKey="date" tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} minTickGap={50} />
                <YAxis tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Line type="monotone" dataKey="profit" stroke="#7c9473" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </Panel>

          {summary.expenses.total_expenses > 0 && (
            <div className="two-col">
              <Panel title="Expenses by category">
                <ResponsiveContainer width="100%" height={240}>
                  <PieChart>
                    <Pie
                      data={summary.expenses.by_category}
                      dataKey="amount" nameKey="category"
                      innerRadius={55} outerRadius={90}
                    >
                      {summary.expenses.by_category.map((_, i) => (
                        <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={tooltipStyle} />
                    <Legend wrapperStyle={{ fontSize: 11 }} />
                  </PieChart>
                </ResponsiveContainer>
              </Panel>

              <Panel title="Monthly expenses">
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={summary.expenses.monthly_expenses}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--panel-border)" />
                    <XAxis dataKey="month" tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                    <YAxis tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                    <Tooltip contentStyle={tooltipStyle} />
                    <Bar dataKey="amount" fill="#c1503a" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </Panel>
            </div>
          )}

          <div className="two-col">
            <Panel title="Top products">
              <ResponsiveContainer width="100%" height={260}>
                <BarChart data={summary.charts.top_products} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--panel-border)" />
                  <XAxis type="number" tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                  <YAxis dataKey="product" type="category" width={90} tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="orders" fill="#e8c468" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Panel>

            <Panel title="Revenue distribution">
              <ResponsiveContainer width="100%" height={260}>
                <PieChart>
                  <Pie
                    data={summary.charts.product_revenue}
                    dataKey="revenue" nameKey="product"
                    innerRadius={55} outerRadius={90}
                  >
                    {summary.charts.product_revenue.map((_, i) => (
                      <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={tooltipStyle} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                </PieChart>
              </ResponsiveContainer>
            </Panel>
          </div>

          <Panel title="Recent sales">
            <RecentSalesTable rows={summary.recent_sales} />
          </Panel>
        </>
      )}
    </div>
  )
}

function PageHeader({ title, subtitle }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <h1 style={{ fontSize: 30 }}>{title}</h1>
      <p style={{ color: 'var(--flour-dim)', marginTop: 6 }}>{subtitle}</p>
    </div>
  )
}

function SummaryLine({ label: l, value, warn, last }) {
  return (
    <div style={{
      display: 'flex', justifyContent: 'space-between',
      padding: '9px 0', borderBottom: last ? 'none' : '1px dashed var(--panel-border)',
    }}>
      <span style={{ color: 'var(--flour-dim)', fontSize: 13 }}>{l}</span>
      <span className="num" style={{ fontSize: 13, color: warn ? 'var(--jam)' : 'var(--flour)' }}>{value}</span>
    </div>
  )
}

function RecentSalesTable({ rows }) {
  return (
    <div style={{ overflowX: 'auto' }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr>
            {['Product', 'Revenue', 'Cost', 'Profit', 'Date'].map(h => (
              <th key={h} style={{ textAlign: 'left', padding: '8px 10px', color: 'var(--flour-dim)', fontSize: 11, textTransform: 'uppercase', borderBottom: '1px solid var(--panel-border)' }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <td style={{ padding: '9px 10px', borderBottom: '1px solid var(--panel-border)' }}>{r.product_name}</td>
              <td className="num" style={{ padding: '9px 10px', borderBottom: '1px solid var(--panel-border)' }}>{money(r.revenue)}</td>
              <td className="num" style={{ padding: '9px 10px', borderBottom: '1px solid var(--panel-border)' }}>{money(r.cost)}</td>
              <td className="num" style={{ padding: '9px 10px', borderBottom: '1px solid var(--panel-border)', color: 'var(--sage)' }}>{money(r.profit)}</td>
              <td style={{ padding: '9px 10px', borderBottom: '1px solid var(--panel-border)', color: 'var(--flour-dim)' }}>{r.sale_date}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function RecentOrdersList({ rows }) {
  if (rows.length === 0) {
    return <div style={{ color: 'var(--flour-dim)', fontSize: 13 }}>No recent orders.</div>
  }
  return (
    <div style={{ display: 'grid', gap: 10 }}>
      {rows.map(o => (
        <div key={o.id} style={listRow.row}>
          <div>
            <div style={{ fontSize: 13 }}>{o.product_name}</div>
            <div style={{ fontSize: 11, color: 'var(--flour-dim)' }}>{o.quantity} units · {o.order_date}</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div className="num" style={{ fontSize: 13 }}>{money(o.selling_price * o.quantity)}</div>
            <div style={{ fontSize: 11, color: 'var(--flour-dim)', textTransform: 'capitalize' }}>{o.delivery_status || 'pending'}</div>
          </div>
        </div>
      ))}
    </div>
  )
}

function RecentExpensesList({ rows }) {
  if (rows.length === 0) {
    return <div style={{ color: 'var(--flour-dim)', fontSize: 13 }}>Your expenses will appear here.</div>
  }
  return (
    <div style={{ display: 'grid', gap: 10 }}>
      {rows.map(e => (
        <div key={e.id} style={listRow.row}>
          <div>
            <div style={{ fontSize: 13 }}>{e.description}</div>
            <div style={{ fontSize: 11, color: 'var(--flour-dim)' }}>{e.category} · {e.expense_date}</div>
          </div>
          <div className="num" style={{ fontSize: 13, color: 'var(--jam)' }}>{money(e.amount)}</div>
        </div>
      ))}
    </div>
  )
}

const listRow = {
  row: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 0',
    borderBottom: '1px dashed var(--panel-border)',
  },
}

const tooltipStyle = {
  background: 'var(--charcoal-soft)',
  border: '1px solid var(--panel-border)',
  borderRadius: 8,
  fontSize: 12,
}

const styles = {
  filterRow: { display: 'flex', gap: 16, marginBottom: 24, flexWrap: 'wrap' },
}