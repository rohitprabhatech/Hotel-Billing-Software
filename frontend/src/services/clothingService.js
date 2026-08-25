import apiClient from './apiClient';

export async function fetchClothingPosCatalog(params = {}) {
  const { data } = await apiClient.get('/clothing/pos-catalog', { params });
  return data;
}

export async function fetchClothingSales(params = {}) {
  const { data } = await apiClient.get('/clothing/sales', { params });
  return data;
}

export async function fetchClothingCustomerHistory(customerId, params = {}) {
  const { data } = await apiClient.get('/clothing/customer-history', {
    params: { customer_id: customerId, ...params },
  });
  return data;
}
