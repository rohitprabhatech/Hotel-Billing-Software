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

export async function sendBillWhatsapp(billId, payload = {}) {
  const { data } = await apiClient.post(`/bills/${billId}/send-whatsapp`, payload);
  return data;
}

export async function sendBillEmail(billId, payload = {}) {
  const { data } = await apiClient.post(`/bills/${billId}/send-email`, payload);
  return data;
}

export async function downloadBillPdf(billId, billNumber = 'bill') {
  const response = await apiClient.get(`/bills/${billId}/pdf`, { responseType: 'blob' });
  const blob = new Blob([response.data], { type: 'application/pdf' });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${billNumber || 'bill'}.pdf`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
}