import apiClient from './apiClient';

export async function listOrders(params = {}) {
  const { data } = await apiClient.get('/orders', { params });
  return data;
}

export async function getOrder(id) {
  const { data } = await apiClient.get(`/orders/${id}`);
  return data;
}

export async function createOrder(payload) {
  const { data } = await apiClient.post('/orders', payload);
  return data;
}

export async function cancelOrder(id, reason = null) {
  const body = reason ? { reason } : {};
  const { data } = await apiClient.post(`/orders/${id}/cancel`, body);
  return data;
}

export async function addOrderItem(orderId, payload) {
  const { data } = await apiClient.post(`/orders/${orderId}/items`, payload);
  return data;
}

export async function updateOrderItem(orderId, lineId, payload) {
  const { data } = await apiClient.patch(`/orders/${orderId}/items/${lineId}`, payload);
  return data;
}

export async function removeOrderItem(orderId, lineId) {
  const { data } = await apiClient.delete(`/orders/${orderId}/items/${lineId}`);
  return data;
}
