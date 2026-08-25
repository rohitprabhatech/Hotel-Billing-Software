import apiClient from './apiClient';

export async function listItemImages(itemId) {
  const { data } = await apiClient.get(`/items/${itemId}/images`);
  return data;
}

export async function createItemImage(itemId, payload) {
  const { data } = await apiClient.post(`/items/${itemId}/images`, payload);
  return data;
}

export async function uploadItemImage(itemId, file, extra = {}) {
  const form = new FormData();
  form.append('file', file);
  if (extra.variant_id) form.append('variant_id', extra.variant_id);
  if (extra.alt_text) form.append('alt_text', extra.alt_text);
  if (extra.is_primary) form.append('is_primary', 'true');
  const { data } = await apiClient.post(`/items/${itemId}/images/upload`, form);
  return data;
}

export async function deleteItemImage(itemId, imageId) {
  const { data } = await apiClient.delete(`/items/${itemId}/images/${imageId}`);
  return data;
}
