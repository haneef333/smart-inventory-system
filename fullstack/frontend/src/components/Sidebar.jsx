import { NavLink } from 'react-router-dom'

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: '◈' },
  { to: '/inventory', label: 'Inventory', icon: '▤' },
  { to: '/recipes', label: 'Recipes', icon: '✎' },
  { to: '/orders', label: 'Orders', icon: '⌗' },
  { to: '/forecast', label: 'Forecast', icon: '↗' },
]

export default function Sidebar() {
  return (
    <aside style={styles.sidebar}>
      <div style={styles.brand}>
        <div style={styles.brandMark}>C&amp;L</div>
        <div>
          <div style={styles.brandName}>Crumb &amp; Ledger</div>
          <div className="eyebrow" style={{ color: 'var(--flour-dim)' }}>inventory &amp; forecast</div>
        </div>
      </div>

      <nav style={styles.nav}>
        {NAV_ITEMS.map(item => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            style={({ isActive }) => ({
              ...styles.navLink,
              ...(isActive ? styles.navLinkActive : {}),
            })}
          >
            <span style={styles.navIcon}>{item.icon}</span>
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div style={styles.footer}>
        <div className="eyebrow">status</div>
        <div style={styles.footerLine}>
          <span style={styles.dot} /> API connected
        </div>
      </div>
    </aside>
  )
}

const styles = {
  sidebar: {
    width: 232,
    minWidth: 232,
    height: '100vh',
    position: 'sticky',
    top: 0,
    background: 'var(--charcoal-soft)',
    borderRight: '1px solid var(--panel-border)',
    display: 'flex',
    flexDirection: 'column',
    padding: '24px 16px',
  },
  brand: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '4px 8px 28px',
    borderBottom: '1px dashed var(--panel-border)',
    marginBottom: 20,
  },
  brandMark: {
    width: 36,
    height: 36,
    borderRadius: 8,
    background: 'linear-gradient(155deg, var(--amber), #8f5326)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontFamily: 'var(--font-display)',
    fontWeight: 700,
    fontSize: 14,
    color: 'var(--charcoal)',
    flexShrink: 0,
  },
  brandName: {
    fontFamily: 'var(--font-display)',
    fontSize: 16,
    fontWeight: 600,
    lineHeight: 1.2,
  },
  nav: {
    display: 'flex',
    flexDirection: 'column',
    gap: 2,
  },
  navLink: {
    display: 'flex',
    alignItems: 'center',
    gap: 10,
    padding: '10px 12px',
    borderRadius: 8,
    textDecoration: 'none',
    color: 'var(--flour-dim)',
    fontSize: 14,
    fontWeight: 500,
    transition: 'background 0.15s ease, color 0.15s ease',
  },
  navLinkActive: {
    background: 'var(--panel)',
    color: 'var(--butter)',
  },
  navIcon: {
    width: 18,
    textAlign: 'center',
    fontSize: 14,
    opacity: 0.85,
  },
  footer: {
    marginTop: 'auto',
    paddingTop: 16,
    borderTop: '1px dashed var(--panel-border)',
  },
  footerLine: {
    fontSize: 12,
    color: 'var(--flour-dim)',
    display: 'flex',
    alignItems: 'center',
    gap: 6,
    marginTop: 4,
  },
  dot: {
    width: 6,
    height: 6,
    borderRadius: '50%',
    background: 'var(--sage)',
    display: 'inline-block',
  },
}
