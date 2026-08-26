import apiClient from './apiClient';

export async function listDeliveries(params = {}) {
  const { data } = await apiClient.get('/deliveries', { params });
  return data;
}

export async function getDelivery(deliveryId) {
  const { data } = await apiClient.get(`/deliveries/${deliveryId}`);
  return data;
}

export async function createDelivery(payload) {
  const { data } = await apiClient.post('/deliveries', payload);
  return data;
}

export async function updateDeliveryStatus(deliveryId, payload) {
  const { data } = await apiClient.patch(`/deliveries/${deliveryId}/status`, payload);
  return data;
}
