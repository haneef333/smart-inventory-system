import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Dashboard from './pages/Dashboard'
import Inventory from './pages/Inventory'
import Recipes from './pages/Recipes'
import Orders from './pages/Orders'
import Forecast from './pages/Forecast'

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ display: 'flex' }}>
        <Sidebar />
        <main style={{ flex: 1, padding: '28px 36px', maxWidth: 1280 }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/inventory" element={<Inventory />} />
            <Route path="/recipes" element={<Recipes />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/forecast" element={<Forecast />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}
