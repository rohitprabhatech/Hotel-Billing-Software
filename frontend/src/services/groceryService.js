import apiClient from './apiClient';

export async function fetchGroceryPosCatalog(params = {}) {
  const { data } = await apiClient.get('/grocery/pos-catalog', { params });
  return data;
}

export async function fetchGroceryOutstanding(params = {}) {
  const { data } = await apiClient.get('/grocery/outstanding', { params });
  return data;
}

export async function fetchGroceryCredit(customerId, params = {}) {
  const { data } = await apiClient.get(`/grocery/credit/${customerId}`, { params });
  return data;
}

export async function payGroceryCredit(customerId, payload) {
  const { data } = await apiClient.post(`/grocery/credit/${customerId}/pay`, payload);
  return data;
}

export async function fetchGrocerySales(params = {}) {
  const { data } = await apiClient.get('/grocery/sales', { params });
  return data;
}
