import apiClient from './apiClient';

export async function listWastage(params = {}) {
  const { data } = await apiClient.get('/wastage', { params });
  return data;
}

export async function getWastage(id) {
  const { data } = await apiClient.get(`/wastage/${id}`);
  return data;
}

export async function createWastage(payload) {
  const { data } = await apiClient.post('/wastage', payload);
  return data;
}
