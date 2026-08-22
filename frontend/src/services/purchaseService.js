import apiClient from './apiClient';

export async function listPurchases(params = {}) {
  const { data } = await apiClient.get('/purchases', { params });
  return data;
}

export async function getPurchase(purchaseId) {
  const { data } = await apiClient.get(`/purchases/${purchaseId}`);
  return data;
}

export async function createPurchase(payload) {
  const { data } = await apiClient.post('/purchases', payload);
  return data;
}

export async function cancelPurchase(purchaseId, reason) {
  const { data } = await apiClient.post(`/purchases/${purchaseId}/cancel`, { reason });
  return data;
}
