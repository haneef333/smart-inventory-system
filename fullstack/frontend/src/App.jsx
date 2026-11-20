import { useCallback, useEffect, useState } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { getAuthStatus, ownerToken } from './api/client'
import OwnerLogin from './components/OwnerLogin'
import Sidebar from './components/Sidebar'
import BottomNav from './components/BottomNav'
import Dashboard from './pages/Dashboard'
import Inventory from './pages/Inventory'
import Recipes from './pages/Recipes'
import Orders from './pages/Orders'
import Forecast from './pages/Forecast'
import Expenses from './pages/Expenses'
import ShoppingList from './pages/ShoppingList'
import Portfolio from './pages/Portfolio'
import OnlineOrders from './pages/OnlineOrders'
import OnlineOrdersBanner from './components/OnlineOrdersBanner'

export default function App() {
  // 'checking' until we know whether the backend has a password set
  const [auth, setAuth] = useState({ state: 'checking', required: false })

  useEffect(() => {
    getAuthStatus()
      .then(({ auth_required }) => setAuth({ required: auth_required, state: auth_required && !ownerToken.get() ? 'login' : 'ok' }))
      .catch(() => setAuth({ required: false, state: 'ok' })) // older backend or offline: carry on as before
    const onLoggedOut = () => setAuth(a => ({ ...a, state: 'login' }))
    window.addEventListener('owner:logged-out', onLoggedOut)
    return () => window.removeEventListener('owner:logged-out', onLoggedOut)
  }, [])

  const logout = useCallback(() => {
    ownerToken.set(null)
    setAuth(a => ({ ...a, state: 'login' }))
  }, [])

  if (auth.state === 'checking') return null
  if (auth.state === 'login') return <OwnerLogin onLoggedIn={() => setAuth(a => ({ ...a, state: 'ok' }))} />

  return (
    <BrowserRouter>
      <div style={{ display: 'flex' }}>
        <div className="desktop-sidebar">
          <Sidebar onLogout={auth.required ? logout : null} />
        </div>
        <main className="app-main" style={{ flex: 1, padding: '28px 36px', maxWidth: 1280 }}>
          <OnlineOrdersBanner />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/recipes" element={<Recipes />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/online-orders" element={<OnlineOrders />} />
            <Route path="/forecast" element={<Forecast />} />
            <Route path="/expenses" element={<Expenses />} />
            <Route path="/shopping-list" element={<ShoppingList />} />
            <Route path="/portfolio" element={<Portfolio />} />
          </Routes>
        </main>
        <BottomNav />
      </div>
    </BrowserRouter>
  )
}
