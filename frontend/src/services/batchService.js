import apiClient from './apiClient';

export async function listBatches(params = {}) {
  const { data } = await apiClient.get('/batches', { params });
  return data;
}

export async function fetchExpiryReport(params = {}) {
  const { data } = await apiClient.get('/batches/expiry', { params });
  return data;
}

export async function createBatch(payload) {
  const { data } = await apiClient.post('/batches', payload);
  return data;
}

export async function adjustBatch(batchId, payload) {
  const { data } = await apiClient.post(`/batches/${batchId}/adjust`, payload);
  return data;
}
