import apiClient from './apiClient';

export async function fetchSupplierOutstanding(params = {}) {
  const { data } = await apiClient.get('/suppliers/outstanding', { params });
  return data;
}

export async function fetchSupplierLedger(supplierId, params = {}) {
  const { data } = await apiClient.get(`/suppliers/${supplierId}/ledger`, { params });
  return data;
}

export async function paySupplierCredit(supplierId, payload) {
  const { data } = await apiClient.post(`/suppliers/${supplierId}/payments`, payload);
  return data;
}
