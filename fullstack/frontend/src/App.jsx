import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import BottomNav from './components/BottomNav'
import Dashboard from './pages/Dashboard'
import Inventory from './pages/Inventory'
import Recipes from './pages/Recipes'
import Orders from './pages/Orders'
import Forecast from './pages/Forecast'
import Expenses from './pages/Expenses'
import ShoppingList from './pages/ShoppingList'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex' }}>
        <div className="desktop-sidebar">
          <Sidebar />
        </div>
        <main className="app-main" style={{ flex: 1, padding: '28px 36px', maxWidth: 1280 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/recipes" element={<Recipes />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/forecast" element={<Forecast />} />
            <Route path="/expenses" element={<Expenses />} />
            <Route path="/shopping-list" element={<ShoppingList />} />
          </Routes>
        </main>
        <BottomNav />
      </div>
    </BrowserRouter>
  )
}
