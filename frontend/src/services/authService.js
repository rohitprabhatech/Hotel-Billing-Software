import apiClient from './apiClient';

export async function loginRequest(email, password) {
  const { data } = await apiClient.post('/auth/login', { email, password });
  return data;
}

export async function logoutRequest() {
  const { data } = await apiClient.post('/auth/logout');
  return data;
}

export async function fetchMe() {
  const { data } = await apiClient.get('/auth/me');
  return data;
}