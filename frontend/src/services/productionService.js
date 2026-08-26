import apiClient from './apiClient';

export async function listProductions(params = {}) {
  const { data } = await apiClient.get('/productions', { params });
  return data;
}

export async function getProduction(id) {
  const { data } = await apiClient.get(`/productions/${id}`);
  return data;
}

export async function createProduction(payload) {
  const { data } = await apiClient.post('/productions', payload);
  return data;
}
