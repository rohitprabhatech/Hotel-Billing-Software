import apiClient from './apiClient';

export async function listSalesOrders(params = {}) {
  const { data } = await apiClient.get('/sales-orders', { params });
  return data;
}

export async function createSalesOrder(payload) {
  const { data } = await apiClient.post('/sales-orders', payload);
  return data;
}

export async function updateSalesOrderStatus(orderId, payload) {
  const { data } = await apiClient.patch(`/sales-orders/${orderId}/status`, payload);
  return data;
}

export async function convertSalesOrder(orderId, payload = {}) {
  const { data } = await apiClient.post(`/sales-orders/${orderId}/convert`, payload);
  return data;
}

export async function listPurchaseOrders(params = {}) {
  const { data } = await apiClient.get('/purchase-orders', { params });
  return data;
}

export async function createPurchaseOrder(payload) {
  const { data } = await apiClient.post('/purchase-orders', payload);
  return data;
}

export async function updatePurchaseOrderStatus(orderId, payload) {
  const { data } = await apiClient.patch(`/purchase-orders/${orderId}/status`, payload);
  return data;
}

export async function convertPurchaseOrder(orderId, payload = {}) {
  const { data } = await apiClient.post(`/purchase-orders/${orderId}/convert`, payload);
  return data;
}
