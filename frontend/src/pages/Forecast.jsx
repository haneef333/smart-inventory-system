import { useEffect, useState } from 'react'
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { getForecastProducts, getForecast } from '../api/client'
import Panel from '../components/Panel'
import TicketCard from '../components/TicketCard'
import { input, label, field, table, th, td, badge } from '../components/ui'

export default function Forecast() {
  const [products, setProducts] = useState([])
  const [selected, setSelected] = useState('')
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    getForecastProducts().then(list => {
      setProducts(list)
      setSelected(list[0] || '')
    })
  }, [])

  useEffect(() => {
    if (!selected) return
    setLoading(true); setError(null); setData(null)
    getForecast(selected)
      .then(setData)
      .catch(err => setError(err?.response?.data?.detail || 'Forecast failed.'))
      .finally(() => setLoading(false))
  }, [selected])

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 30 }}>Forecast</h1>
        <p style={{ color: 'var(--flour-dim)', marginTop: 6 }}>Demand prediction from real historical sales — Moving Average vs XGBoost vs Prophet</p>
      </div>

      <div style={{ ...field, width: 280, marginBottom: 20 }}>
        <label style={label}>Product</label>
        <select style={input} value={selected} onChange={e => setSelected(e.target.value)}>
          {products.map(p => <option key={p} value={p}>{p}</option>)}
        </select>
      </div>

      {loading && <div className="eyebrow">Training models…</div>}
      {error && (
        <Panel><div style={{ color: 'var(--jam)' }}>{error}</div></Panel>
      )}

      {data && !loading && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 16, marginBottom: 20 }}>
            <TicketCard eyebrow="Last actual demand" value={data.last_actual} accent="butter" />
            <TicketCard
              eyebrow="Trend"
              value={data.trend === 'increasing' ? '↑ Increasing' : '↓ Decreasing'}
              accent={data.trend === 'increasing' ? 'sage' : 'jam'}
            />
            <TicketCard eyebrow="Best model" value={data.best_model} accent="amber" />
          </div>

          {!data.prophet_available && (
            <div style={{ padding: '10px 14px', borderRadius: 8, marginBottom: 20, background: 'rgba(232,196,104,0.08)', border: '1px solid rgba(232,196,104,0.3)', color: 'var(--butter)', fontSize: 13 }}>
              Prophet isn't installed on this server, so results below compare Moving Average and XGBoost only. Install the <code>prophet</code> package on the backend to add it.
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
            <Panel title="Model comparison">
              <table style={table}>
                <thead>
                  <tr>{['Model', 'Prediction'].map(h => <th key={h} style={th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {data.models.map(m => (
                    <tr key={m.model}>
                      <td style={td}>
                        {m.model}
                        {m.model === data.best_model && <span style={{ ...badge('var(--sage)'), marginLeft: 8 }}>best</span>}
                      </td>
                      <td style={td} className="num">{m.prediction}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Panel>

            <Panel title="Model evaluation">
              <table style={table}>
                <thead>
                  <tr>{['Model', 'RMSE', 'SMAPE %'].map(h => <th key={h} style={th}>{h}</th>)}</tr>
                </thead>
                <tbody>
                  {data.models.map(m => (
                    <tr key={m.model}>
                      <td style={td}>{m.model}</td>
                      <td style={td} className="num">{m.rmse}</td>
                      <td style={td} className="num">{m.smape}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div style={{ marginTop: 10, fontSize: 12, color: 'var(--flour-dim)' }}>
                Train: {data.train_days} days · Test: {data.test_days} days (30-day holdout)
              </div>
            </Panel>
          </div>

          <Panel title="Historical demand">
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={data.history}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--panel-border)" />
                <XAxis dataKey="ds" tick={{ fontSize: 10, fill: 'var(--flour-dim)' }} minTickGap={40} />
                <YAxis tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                <Tooltip contentStyle={tooltipStyle} />
                <Line type="monotone" dataKey="y" stroke="#c17a3d" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </Panel>

          <div style={{ marginTop: 20 }}>
            <Panel title="XGBoost feature importance">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={data.feature_importance} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--panel-border)" />
                  <XAxis type="number" tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                  <YAxis dataKey="feature" type="category" width={110} tick={{ fontSize: 11, fill: 'var(--flour-dim)' }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Bar dataKey="importance" fill="#e8c468" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Panel>
          </div>
        </>
      )}
    </div>
  )
}

const tooltipStyle = {
  background: 'var(--charcoal-soft)',
  border: '1px solid var(--panel-border)',
  borderRadius: 8,
  fontSize: 12,
}
