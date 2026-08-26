import apiClient from './apiClient';

export async function listPriceLists(params = {}) {
  const { data } = await apiClient.get('/price-lists', { params });
  return data;
}

export async function getPriceList(priceListId) {
  const { data } = await apiClient.get(`/price-lists/${priceListId}`);
  return data;
}

export async function createPriceList(payload) {
  const { data } = await apiClient.post('/price-lists', payload);
  return data;
}

export async function updatePriceList(priceListId, payload) {
  const { data } = await apiClient.patch(`/price-lists/${priceListId}`, payload);
  return data;
}

export async function deletePriceList(priceListId) {
  const { data } = await apiClient.delete(`/price-lists/${priceListId}`);
  return data;
}

export async function replacePriceListItems(priceListId, items) {
  const { data } = await apiClient.put(`/price-lists/${priceListId}/items`, { items });
  return data;
}

export async function listCustomerPriceAssignments(params = {}) {
  const { data } = await apiClient.get('/price-lists/customer-assignments', { params });
  return data;
}

export async function assignCustomerPriceList(customerId, priceListId) {
  const { data } = await apiClient.put(`/price-lists/customer-assignments/${customerId}`, {
    price_list_id: priceListId,
  });
  return data;
}

export async function unassignCustomerPriceList(customerId) {
  const { data } = await apiClient.delete(`/price-lists/customer-assignments/${customerId}`);
  return data;
}
