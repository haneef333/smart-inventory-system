import { NavLink } from 'react-router-dom'

const TABS = [
  { to: '/shopping-list', label: 'Shopping', icon: '🛒' },
  { to: '/expenses', label: 'Expenses', icon: '🧾' },
  { to: '/', label: 'Home', icon: '⌂', isHome: true },
  { to: '/orders', label: 'Orders', icon: '🎂' },
  { to: '/inventory', label: 'Inventory', icon: '👤' },
]

export default function BottomNav() {
  return (
    <nav className="bottom-nav">
      {TABS.map(tab => (
        <NavLink
          key={tab.to}
          to={tab.to}
          end={tab.to === '/'}
          className={({ isActive }) => `bottom-nav-item${isActive ? ' active' : ''}${tab.isHome ? ' home' : ''}`}
        >
          <span className="bottom-nav-icon">{tab.icon}</span>
          <span className="bottom-nav-label">{tab.label}</span>
        </NavLink>
      ))}
    </nav>
  )
}
