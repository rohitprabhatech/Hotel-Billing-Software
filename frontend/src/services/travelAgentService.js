import apiClient from './apiClient';

export async function listTravelAgents(params = {}) {
  const { data } = await apiClient.get('/travel/agents', { params });
  return data;
}

export async function createTravelAgent(payload) {
  const { data } = await apiClient.post('/travel/agents', payload);
  return data;
}

export async function updateTravelAgent(agentId, payload) {
  const { data } = await apiClient.patch(`/travel/agents/${agentId}`, payload);
  return data;
}

export async function deleteTravelAgent(agentId) {
  const { data } = await apiClient.delete(`/travel/agents/${agentId}`);
  return data;
}

export async function listTravelCommissions(params = {}) {
  const { data } = await apiClient.get('/travel/commissions', { params });
  return data;
}

export async function getTravelCommissionReport() {
  const { data } = await apiClient.get('/travel/commissions/report');
  return data;
}

export async function createTravelCommission(payload) {
  const { data } = await apiClient.post('/travel/commissions', payload);
  return data;
}

export async function updateTravelCommissionStatus(entryId, payload) {
  const { data } = await apiClient.patch(`/travel/commissions/${entryId}/status`, payload);
  return data;
}
