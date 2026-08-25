import apiClient from './apiClient';

export async function lookupReturnBill(params = {}) {
  const { data } = await apiClient.get('/returns/lookup', { params });
  return data;
}

export async function listReturns(params = {}) {
  const { data } = await apiClient.get('/returns', { params });
  return data;
}

export async function createReturn(payload) {
  const { data } = await apiClient.post('/returns', payload);
  return data;
}
