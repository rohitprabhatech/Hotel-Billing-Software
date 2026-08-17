import apiClient from './apiClient';

export async function listStockMovements(params = {}) {
  const { data } = await apiClient.get('/stock-movements', { params });
  return data;
}
