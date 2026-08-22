import apiClient from './apiClient';

export async function fetchGroceryPosCatalog(params = {}) {
  const { data } = await apiClient.get('/grocery/pos-catalog', { params });
  return data;
}
