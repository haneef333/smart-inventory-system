import { useReveal } from '../hooks/useReveal'

export default function TicketCard({ eyebrow, value, accent }) {
  const [ref, visible] = useReveal()

  return (
    <div
      ref={ref}
      className={`reveal ticket-card${visible ? ' reveal-in' : ''}`}
      style={{ ...cardStyle, borderTop: `3px solid var(--${accent})` }}
    >
      <div style={eyebrowStyle}>{eyebrow}</div>
      <div className="num" style={valueStyle}>{value}</div>
    </div>
  )
}

const cardStyle = {
  background: 'var(--panel)',
  border: '1px solid var(--panel-border)',
  borderRadius: 14,
  padding: '18px 20px',
}

const eyebrowStyle = {
  fontSize: 12,
  color: 'var(--flour-dim)',
  textTransform: 'uppercase',
  letterSpacing: '0.03em',
  marginBottom: 8,
}

const valueStyle = {
  fontSize: 24,
  fontWeight: 600,
}
