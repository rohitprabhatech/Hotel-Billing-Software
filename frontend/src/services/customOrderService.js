import apiClient from './apiClient';

export async function listCustomOrders(params = {}) {
  const { data } = await apiClient.get('/custom-orders', { params });
  return data;
}

export async function getCustomOrder(id) {
  const { data } = await apiClient.get(`/custom-orders/${id}`);
  return data;
}

export async function createCustomOrder(payload) {
  const { data } = await apiClient.post('/custom-orders', payload);
  return data;
}

export async function updateCustomOrderStatus(id, payload) {
  const { data } = await apiClient.patch(`/custom-orders/${id}/status`, payload);
  return data;
}

export async function recordCustomOrderAdvance(id, payload) {
  const { data } = await apiClient.post(`/custom-orders/${id}/advance`, payload);
  return data;
}
