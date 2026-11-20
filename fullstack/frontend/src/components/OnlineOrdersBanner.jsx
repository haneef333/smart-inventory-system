import { useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useOnlineOrderSummary } from '../hooks/useOnlineOrderSummary'

// Shown on every page (including phones, where there is no sidebar) while
// storefront orders need attention.
export default function OnlineOrdersBanner() {
  const { new: newCount, active } = useOnlineOrderSummary()
  const { pathname } = useLocation()

  useEffect(() => {
    const base = document.title.replace(/^\(\d+\) /, '')
    document.title = newCount > 0 ? `(${newCount}) ${base}` : base
  }, [newCount])

  if (pathname === '/online-orders' || (newCount === 0 && active === 0)) return null

  const parts = []
  if (newCount) parts.push(`${newCount} new online order${newCount > 1 ? 's' : ''} to review`)
  if (active) parts.push(`${active} in progress`)

  return (
    <Link to="/online-orders" style={{ ...bannerStyle, ...(newCount ? newStyle : {}) }}>
      <span>{newCount ? '🔔' : '🧁'} {parts.join(', ')}</span>
      <span style={{ fontWeight: 600 }}>Open online orders</span>
    </Link>
  )
}

const bannerStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  gap: 12,
  flexWrap: 'wrap',
  padding: '12px 16px',
  marginBottom: 20,
  borderRadius: 12,
  textDecoration: 'none',
  fontSize: 14,
  background: 'var(--panel)',
  border: '1px solid var(--panel-border)',
  color: 'var(--flour)',
}

const newStyle = {
  background: 'rgba(232, 196, 104, 0.12)',
  border: '1px solid rgba(232, 196, 104, 0.5)',
  color: 'var(--butter)',
}
