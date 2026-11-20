import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

// ---- Owner login ----
// The token is kept in this browser. Every request sends it; if the backend
// says "please log in" (401), the app shows the login screen again.
const TOKEN_KEY = 'owner_token'
export const ownerToken = {
  get() { try { return localStorage.getItem(TOKEN_KEY) } catch { return null } },
  set(t) { try { t ? localStorage.setItem(TOKEN_KEY, t) : localStorage.removeItem(TOKEN_KEY) } catch { /* ignore */ } },
}

api.interceptors.request.use(config => {
  const token = ownerToken.get()
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(
  res => res,
  err => {
    if (err?.response?.status === 401 && !err.config?.url?.startsWith('/auth/')) {
      ownerToken.set(null)
      window.dispatchEvent(new Event('owner:logged-out'))
    }
    return Promise.reject(err)
  },
)

export const getAuthStatus = () => api.get('/auth/status').then(r => r.data)
export const ownerLogin = (password) => api.post('/auth/login', { password }).then(r => r.data)

// WebSocket address for live order alerts, e.g. ws://127.0.0.1:8000/api/online-orders/ws
export function onlineOrdersSocketUrl() {
  const base = import.meta.env.VITE_API_URL || `${window.location.origin}/api`
  const url = new URL(`${base.replace(/\/$/, '')}/online-orders/ws`, window.location.origin)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  const token = ownerToken.get()
  if (token) url.searchParams.set('token', token)
  return url.toString()
}

export default api

export const getInventory = () => api.get('/inventory').then(r => r.data)
export const addInventoryItem = (item) => api.post('/inventory', item).then(r => r.data)
export const restockItem = (id, add_quantity) =>
  api.patch(`/inventory/${id}/restock`, { add_quantity }).then(r => r.data)
export const deleteInventoryItem = (id) => api.delete(`/inventory/${id}`).then(r => r.data)

export const getRecipes = () => api.get('/recipes').then(r => r.data)
export const getProducts = () => api.get('/recipes/products').then(r => r.data)
export const getRecipe = (productName) =>
  api.get(`/recipes/${encodeURIComponent(productName)}`).then(r => r.data)
export const addRecipeLine = (line) => api.post('/recipes', line).then(r => r.data)

export const getOrders = () => api.get('/orders').then(r => r.data)
export const placeOrder = (order) => api.post('/orders', order).then(r => r.data)
export const updateOrderStatus = (id, update) =>
  api.patch(`/orders/${id}/status`, update).then(r => r.data)

export const getExpenses = () => api.get('/expenses').then(r => r.data)
export const getExpenseCategories = () => api.get('/expenses/categories').then(r => r.data)
export const addExpense = (expense) => api.post('/expenses', expense).then(r => r.data)
export const deleteExpense = (id) => api.delete(`/expenses/${id}`).then(r => r.data)

export const getLowStockList = () => api.get('/shopping-list/low-stock').then(r => r.data)
export const generateShoppingList = (payload) =>
  api.post('/shopping-list/generate', payload).then(r => r.data)

export const getDashboardMeta = () => api.get('/dashboard/meta').then(r => r.data)
export const getDashboardSummary = (params) =>
  api.get('/dashboard/summary', { params }).then(r => r.data)

export const getForecastProducts = () => api.get('/forecast/products').then(r => r.data)
export const getForecast = (productName) =>
  api.get(`/forecast/${encodeURIComponent(productName)}`).then(r => r.data)

export const getTasksForMonth = (month) => api.get('/tasks', { params: { month } }).then(r => r.data)
export const getTasksForDate = (date) => api.get('/tasks', { params: { date } }).then(r => r.data)
export const addTask = (task) => api.post('/tasks', task).then(r => r.data)
export const updateTask = (id, update) => api.patch(`/tasks/${id}`, update).then(r => r.data)
export const deleteTask = (id) => api.delete(`/tasks/${id}`).then(r => r.data)

export const getPortfolioItems = () => api.get('/portfolio').then(r => r.data)
export const addPortfolioItem = (title, file) => {
  const formData = new FormData()
  formData.append('title', title)
  formData.append('image', file)
  return api.post('/portfolio', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  }).then(r => r.data)
}
export const deletePortfolioItem = (id) => api.delete(`/portfolio/${id}`).then(r => r.data)
export const portfolioImageUrl = (filename) => `${api.defaults.baseURL.replace(/\/api$/, '')}/uploads/portfolio/${filename}`

// --- Online orders from the customer storefront
export const getOnlineOrders = (status = 'all') => api.get('/online-orders', { params: { status } }).then(r => r.data)
export const getOnlineOrderSummary = () => api.get('/online-orders/summary').then(r => r.data)
export const acceptOnlineOrder = (id) => api.post(`/online-orders/${id}/accept`).then(r => r.data)
export const declineOnlineOrder = (id, reason) => api.post(`/online-orders/${id}/decline`, { reason }).then(r => r.data)
export const updateOnlineOrder = (id, update) => api.patch(`/online-orders/${id}/status`, update).then(r => r.data)
