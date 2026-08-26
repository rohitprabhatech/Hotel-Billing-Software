import apiClient from './apiClient';

export async function listTourPackages(params = {}) {
  const { data } = await apiClient.get('/travel/packages', { params });
  return data;
}

export async function getTourPackage(packageId) {
  const { data } = await apiClient.get(`/travel/packages/${packageId}`);
  return data;
}

export async function createTourPackage(payload) {
  const { data } = await apiClient.post('/travel/packages', payload);
  return data;
}

export async function updateTourPackage(packageId, payload) {
  const { data } = await apiClient.patch(`/travel/packages/${packageId}`, payload);
  return data;
}

export async function billTourPackage(packageId, payload = {}) {
  const { data } = await apiClient.post(`/travel/packages/${packageId}/bill`, payload);
  return data;
}
