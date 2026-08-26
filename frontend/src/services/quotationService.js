import apiClient from './apiClient';

export async function listQuotations(params = {}) {
  const { data } = await apiClient.get('/quotations', { params });
  return data;
}

export async function getQuotation(quotationId) {
  const { data } = await apiClient.get(`/quotations/${quotationId}`);
  return data;
}

export async function createQuotation(payload) {
  const { data } = await apiClient.post('/quotations', payload);
  return data;
}

export async function updateQuotationStatus(quotationId, payload) {
  const { data } = await apiClient.patch(`/quotations/${quotationId}/status`, payload);
  return data;
}

export async function convertQuotation(quotationId, payload = {}) {
  const { data } = await apiClient.post(`/quotations/${quotationId}/convert`, payload);
  return data;
}
