import apiClient from './apiClient';

export async function listSuppliers(params = {}) {
  const { data } = await apiClient.get('/suppliers', { params });
  return data;
}

export async function getSupplier(supplierId) {
  const { data } = await apiClient.get(`/suppliers/${supplierId}`);
  return data;
}

export async function createSupplier(payload) {
  const { data } = await apiClient.post('/suppliers', payload);
  return data;
}

export async function updateSupplier(supplierId, payload) {
  const { data } = await apiClient.patch(`/suppliers/${supplierId}`, payload);
  return data;
}

export async function deactivateSupplier(supplierId) {
  const { data } = await apiClient.delete(`/suppliers/${supplierId}`);
  return data;
}

export async function setSupplierStatus(supplierId, isActive) {
  const { data } = await apiClient.patch(`/suppliers/${supplierId}/status`, {
    is_active: isActive,
  });
  return data;
}
