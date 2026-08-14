import apiClient from './apiClient';

export async function fetchMyTenant() {
  const { data } = await apiClient.get('/tenants/me');
  return data;
}

export async function updateMyTenant(payload) {
  const { data } = await apiClient.put('/tenants/me', payload);
  return data;
}

export async function fetchBusinessTypes() {
  const { data } = await apiClient.get('/tenants/business-types');
  return data;
}