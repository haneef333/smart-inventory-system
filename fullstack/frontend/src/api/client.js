import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
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
