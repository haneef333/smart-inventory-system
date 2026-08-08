export default function TicketCard({ eyebrow, value, sub, accent = 'amber' }) {
  const accentColor = `var(--${accent})`

  return (
    <div style={styles.card}>
      <div style={styles.perfTop} />
      <div style={{ padding: '18px 18px 16px' }}>
        <div className="eyebrow">{eyebrow}</div>
        <div style={{ ...styles.value, color: accentColor }}>{value}</div>
        {sub && <div style={styles.sub}>{sub}</div>}
      </div>
      <div style={styles.perfBottom} />
    </div>
  )
}

const notch = 'radial-gradient(circle at 8px 0, transparent 7px, var(--charcoal) 7px)'

const styles = {
  card: {
    background: 'linear-gradient(180deg, var(--panel), var(--charcoal-soft))',
    border: '1px solid var(--panel-border)',
    borderRadius: 12,
    position: 'relative',
    overflow: 'hidden',
  },
  perfTop: {
    height: 8,
    backgroundImage: notch,
    backgroundSize: '16px 16px',
    backgroundPosition: 'top',
  },
  perfBottom: {
    height: 8,
    backgroundImage: notch,
    backgroundSize: '16px 16px',
    backgroundPosition: 'bottom',
    transform: 'rotate(180deg)',
  },
  value: {
    fontFamily: 'var(--font-mono)',
    fontSize: 28,
    fontWeight: 600,
    marginTop: 8,
    lineHeight: 1.1,
  },
  sub: {
    fontSize: 12,
    color: 'var(--flour-dim)',
    marginTop: 6,
  },
}
