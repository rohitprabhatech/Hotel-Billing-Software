import apiClient from './apiClient';

export async function listCustomers(params = {}) {
  const { data } = await apiClient.get('/customers', { params });
  return data;
}

export async function getCustomer(customerId) {
  const { data } = await apiClient.get(`/customers/${customerId}`);
  return data;
}

export async function createCustomer(payload) {
  const { data } = await apiClient.post('/customers', payload);
  return data;
}

export async function updateCustomer(customerId, payload) {
  const { data } = await apiClient.patch(`/customers/${customerId}`, payload);
  return data;
}

export async function deactivateCustomer(customerId) {
  const { data } = await apiClient.delete(`/customers/${customerId}`);
  return data;
}

export async function setCustomerStatus(customerId, isActive) {
  const { data } = await apiClient.patch(`/customers/${customerId}/status`, {
    is_active: isActive,
  });
  return data;
}

export async function listCustomerBills(customerId, params = {}) {
  const { data } = await apiClient.get(`/customers/${customerId}/bills`, { params });
  return data;
}

export async function listCustomerLedger(customerId, params = {}) {
  const { data } = await apiClient.get(`/customers/${customerId}/ledger`, { params });
  return data;
}

export async function recordCustomerPayment(customerId, payload) {
  const { data } = await apiClient.post(`/customers/${customerId}/payments`, payload);
  return data;
}

export async function listOutstandingCustomers(params = {}) {
  const { data } = await apiClient.get('/customers/outstanding', { params });
  return data;
}
