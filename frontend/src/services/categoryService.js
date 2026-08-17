import apiClient from './apiClient';

export async function listCategories() {
  const { data } = await apiClient.get('/categories');
  return data;
}

export async function createCategory(payload) {
  const { data } = await apiClient.post('/categories', payload);
  return data;
}

export async function updateCategory(id, payload) {
  const { data } = await apiClient.put(`/categories/${id}`, payload);
  return data;
}

export async function setCategoryStatus(id, isActive) {
  const { data } = await apiClient.patch(`/categories/${id}/status`, {
    is_active: isActive,
  });
  return data;
}