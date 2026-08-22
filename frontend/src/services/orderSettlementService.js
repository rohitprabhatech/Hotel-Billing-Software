import apiClient from './apiClient';

export async function settleOrder(orderId, payload) {
  const { data } = await apiClient.post(`/orders/${orderId}/settle`, payload);
  return data;
}

export async function splitOrderBills(payload) {
  const { data } = await apiClient.post('/bills/split', payload);
  return data;
}
