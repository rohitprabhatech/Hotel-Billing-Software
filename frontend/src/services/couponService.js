import apiClient from './apiClient';

export async function listCoupons(params = {}) {
  const { data } = await apiClient.get('/coupons', { params });
  return data;
}

export async function createCoupon(payload) {
  const { data } = await apiClient.post('/coupons', payload);
  return data;
}

export async function updateCoupon(id, payload) {
  const { data } = await apiClient.put(`/coupons/${id}`, payload);
  return data;
}

export async function deactivateCoupon(id) {
  const { data } = await apiClient.delete(`/coupons/${id}`);
  return data;
}

export async function previewCoupon(payload) {
  const { data } = await apiClient.post('/coupons/preview', payload);
  return data;
}
