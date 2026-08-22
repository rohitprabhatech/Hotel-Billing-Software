import apiClient from './apiClient';

export async function listKots(params = {}) {
  const { data } = await apiClient.get('/kots', { params });
  return data;
}

export async function getKitchenQueue() {
  const { data } = await apiClient.get('/kots/kitchen/queue');
  return data;
}

export async function getKot(id) {
  const { data } = await apiClient.get(`/kots/${id}`);
  return data;
}

export async function fireKot(orderId) {
  const { data } = await apiClient.post(`/orders/${orderId}/kot`);
  return data;
}

export async function updateKotStatus(kotId, status) {
  const { data } = await apiClient.patch(`/kots/${kotId}/status`, { status });
  return data;
}
