export const input = {
  width: '100%',
  padding: '9px 11px',
  background: 'var(--charcoal-soft)',
  border: '1px solid var(--panel-border)',
  borderRadius: 8,
  color: 'var(--flour)',
  fontSize: 14,
  outline: 'none',
}

export const label = {
  display: 'block',
  fontSize: 12,
  color: 'var(--flour-dim)',
  marginBottom: 6,
}

export const field = {
  marginBottom: 14,
}

export const buttonPrimary = {
  padding: '10px 18px',
  background: 'var(--amber)',
  color: 'var(--charcoal)',
  border: 'none',
  borderRadius: 8,
  fontWeight: 600,
  fontSize: 14,
  cursor: 'pointer',
}

export const buttonGhost = {
  padding: '9px 16px',
  background: 'transparent',
  color: 'var(--flour)',
  border: '1px solid var(--panel-border)',
  borderRadius: 8,
  fontWeight: 500,
  fontSize: 13,
  cursor: 'pointer',
}

export const buttonDanger = {
  padding: '7px 12px',
  background: 'transparent',
  color: 'var(--jam)',
  border: '1px solid rgba(193,80,58,0.4)',
  borderRadius: 6,
  fontSize: 12,
  cursor: 'pointer',
}

export const table = {
  width: '100%',
  borderCollapse: 'collapse',
  fontSize: 13,
}

export const th = {
  textAlign: 'left',
  padding: '8px 10px',
  color: 'var(--flour-dim)',
  fontSize: 11,
  letterSpacing: '0.06em',
  textTransform: 'uppercase',
  borderBottom: '1px solid var(--panel-border)',
  fontFamily: 'var(--font-mono)',
}

export const td = {
  padding: '10px 10px',
  borderBottom: '1px solid var(--panel-border)',
}

export const badge = (color) => ({
  display: 'inline-block',
  padding: '2px 9px',
  borderRadius: 999,
  fontSize: 11,
  fontWeight: 600,
  background: `${color}22`,
  color: color,
  border: `1px solid ${color}55`,
})
