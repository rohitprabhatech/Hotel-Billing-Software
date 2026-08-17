import apiClient from './apiClient';

export async function listUsers() {
  const { data } = await apiClient.get('/users');
  return data;
}

export async function createBillingUser(payload) {
  const { data } = await apiClient.post('/users', payload);
  return data;
}

export async function updateUser(userId, payload) {
  const { data } = await apiClient.put(`/users/${userId}`, payload);
  return data;
}

export async function resetUserPassword(userId, password) {
  const { data } = await apiClient.patch(`/users/${userId}/password`, { password });
  return data;
}