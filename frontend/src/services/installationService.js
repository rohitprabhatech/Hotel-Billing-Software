import apiClient from './apiClient';

export async function listInstallations(params = {}) {
  const { data } = await apiClient.get('/installations', { params });
  return data;
}

export async function getInstallation(installationId) {
  const { data } = await apiClient.get(`/installations/${installationId}`);
  return data;
}

export async function createInstallation(payload) {
  const { data } = await apiClient.post('/installations', payload);
  return data;
}

export async function updateInstallationStatus(installationId, payload) {
  const { data } = await apiClient.patch(`/installations/${installationId}/status`, payload);
  return data;
}
