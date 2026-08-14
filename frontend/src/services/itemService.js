import apiClient from './apiClient';

export async function listItems(params = {}) {
  const { data } = await apiClient.get('/items', { params });
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
