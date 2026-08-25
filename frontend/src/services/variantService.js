import apiClient from './apiClient';

export async function listTenantVariants(params = {}) {
  const { data } = await apiClient.get('/item-variants', { params });
  return data;
}

export async function listItemVariants(itemId) {
  const { data } = await apiClient.get(`/items/${itemId}/variants`);
  return data;
}

export async function replaceItemVariants(itemId, variants) {
  const { data } = await apiClient.put(`/items/${itemId}/variants`, { variants });
  return data;
}

export async function createItemVariant(itemId, payload) {
  const { data } = await apiClient.post(`/items/${itemId}/variants`, payload);
  return data;
}

export async function deleteItemVariant(itemId, variantId) {
  const { data } = await apiClient.delete(`/items/${itemId}/variants/${variantId}`);
  return data;
}
