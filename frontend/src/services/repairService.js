import apiClient from './apiClient';

export async function listRepairs(params = {}) {
  const { data } = await apiClient.get('/repairs', { params });
  return data;
}

export async function getRepair(repairId) {
  const { data } = await apiClient.get(`/repairs/${repairId}`);
  return data;
}

export async function createRepair(payload) {
  const { data } = await apiClient.post('/repairs', payload);
  return data;
}

export async function updateRepairStatus(repairId, payload) {
  const { data } = await apiClient.patch(`/repairs/${repairId}/status`, payload);
  return data;
}
