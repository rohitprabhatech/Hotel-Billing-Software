import apiClient from './apiClient';

export async function listExpenses(params = {}) {
  const { data } = await apiClient.get('/expenses', { params });
  return data;
}

export async function getExpenseSummary(params = {}) {
  const { data } = await apiClient.get('/expenses/summary', { params });
  return data;
}

export async function getExpense(expenseId) {
  const { data } = await apiClient.get(`/expenses/${expenseId}`);
  return data;
}

export async function createExpense(payload) {
  const { data } = await apiClient.post('/expenses', payload);
  return data;
}

export async function updateExpense(expenseId, payload) {
  const { data } = await apiClient.patch(`/expenses/${expenseId}`, payload);
  return data;
}

export async function deleteExpense(expenseId) {
  const { data } = await apiClient.delete(`/expenses/${expenseId}`);
  return data;
}
