import apiClient from './apiClient';

export async function createBill(payload) {
  const { data } = await apiClient.post('/bills', payload);
  return data;
}

export async function listBills(params = {}) {
  const { data } = await apiClient.get('/bills', { params });
  return data;
}

export async function getBill(billId) {
  const { data } = await apiClient.get(`/bills/${billId}`);
  return data;
}

export async function fetchTodaySummary() {
  const { data } = await apiClient.get('/bills/today-summary');
  return data;
}

export async function cancelBill(billId, reason) {
  const { data } = await apiClient.post(`/bills/${billId}/cancel`, { reason });
  return data;
}

export async function recordBillPrint(billId) {
  const { data } = await apiClient.post(`/bills/${billId}/print`);
  return data;
}

export function openBillPrint(billId, { auto = false } = {}) {
  const url = `/print/bills/${billId}${auto ? '?auto=1' : ''}`;
  window.open(url, '_blank', 'noopener,noreferrer');
}