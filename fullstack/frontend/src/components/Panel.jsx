import { useReveal } from '../hooks/useReveal'

export default function Panel({ title, action, children, style }) {
  const [ref, visible] = useReveal()

  return (
    <section
      ref={ref}
      className={`reveal panel${visible ? ' reveal-in' : ''}`}
      style={{ ...panelStyle, ...style }}
    >
      {(title || action) && (
        <div style={headerStyle}>
          {title && <h3 style={titleStyle}>{title}</h3>}
          {action}
        </div>
      )}
      {children}
    </section>
  )
}

const panelStyle = {
  background: 'var(--panel)',
  border: '1px solid var(--panel-border)',
  borderRadius: 14,
  padding: 20,
}

const headerStyle = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  marginBottom: 16,
}

const titleStyle = {
  fontSize: 16,
  fontWeight: 600,
}
