import apiClient from './apiClient';

export async function listWarehouses(params = {}) {
  const { data } = await apiClient.get('/warehouses', { params });
  return data;
}

export async function createWarehouse(payload) {
  const { data } = await apiClient.post('/warehouses', payload);
  return data;
}

export async function updateWarehouse(warehouseId, payload) {
  const { data } = await apiClient.patch(`/warehouses/${warehouseId}`, payload);
  return data;
}

export async function listWarehouseStocks(params = {}) {
  const { data } = await apiClient.get('/warehouses/stocks', { params });
  return data;
}

export async function listStockTransfers(params = {}) {
  const { data } = await apiClient.get('/stock-transfers', { params });
  return data;
}

export async function createStockTransfer(payload) {
  const { data } = await apiClient.post('/stock-transfers', payload);
  return data;
}
