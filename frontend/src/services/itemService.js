import apiClient from './apiClient';

export async function listItems(params = {}) {
  const { data } = await apiClient.get('/items', { params });
  return data;
}

export async function getItemByBarcode(barcode, params = {}) {
  const encoded = encodeURIComponent(barcode);
  const { data } = await apiClient.get(`/items/by-barcode/${encoded}`, { params });
  return data;
}

export async function createItem(payload) {
  const { data } = await apiClient.post('/items', payload);
  return data;
}

export async function updateItem(id, payload) {
  const { data } = await apiClient.put(`/items/${id}`, payload);
  return data;
}

export async function setItemStatus(id, isActive, reason = null) {
  const body = { is_active: isActive };
  if (reason) body.reason = reason;
  const { data } = await apiClient.patch(`/items/${id}/status`, body);
  return data;
}

export async function adjustItemStock(id, payload) {
  const { data } = await apiClient.post(`/items/${id}/adjust-stock`, payload);
  return data;
}

export async function receiveItemStock(id, payload) {
  const { data } = await apiClient.post(`/items/${id}/receive-stock`, payload);
  return data;
}

export async function listItemPriceTiers(itemId) {
  const { data } = await apiClient.get(`/items/${itemId}/price-tiers`);
  return data;
}

export async function replaceItemPriceTiers(itemId, tiers) {
  const { data } = await apiClient.put(`/items/${itemId}/price-tiers`, { tiers });
  return data;
}

export async function createItemPriceTier(itemId, payload) {
  const { data } = await apiClient.post(`/items/${itemId}/price-tiers`, payload);
  return data;
}

export async function deleteItemPriceTier(itemId, tierId) {
  const { data } = await apiClient.delete(`/items/${itemId}/price-tiers/${tierId}`);
  return data;
}

export async function listItemAccessories(itemId) {
  const { data } = await apiClient.get(`/items/${itemId}/accessories`);
  return data;
}

export async function replaceItemAccessories(itemId, accessoryItemIds) {
  const { data } = await apiClient.put(`/items/${itemId}/accessories`, {
    accessory_item_ids: accessoryItemIds,
  });
  return data;
}
