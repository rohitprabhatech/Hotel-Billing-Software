import apiClient from './apiClient';

export async function fetchMenu(params = {}) {
  const { data } = await apiClient.get('/menu', { params });
  return data;
}
