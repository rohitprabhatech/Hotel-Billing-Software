import apiClient from './apiClient';

export async function fetchMobileSales(params = {}) {
  const { data } = await apiClient.get('/mobile/sales', { params });
  return data;
}

export async function fetchMobileCustomerHistory(customerId, params = {}) {
  const { data } = await apiClient.get('/mobile/customer-history', {
    params: { customer_id: customerId, ...params },
  });
  return data;
}
