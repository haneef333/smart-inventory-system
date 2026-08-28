import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

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
