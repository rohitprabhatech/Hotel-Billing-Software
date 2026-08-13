import apiClient from './apiClient';

export async function fetchMyTenant() {
  const { data } = await apiClient.get('/tenants/me');
  return data;
}

export async function updateMyTenant(payload) {
  const { data } = await apiClient.put('/tenants/me', payload);
  return data;
}