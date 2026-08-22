import apiClient from './apiClient';

export async function listRecipes(params = {}) {
  const { data } = await apiClient.get('/recipes', { params });
  return data;
}

export async function getRecipe(id) {
  const { data } = await apiClient.get(`/recipes/${id}`);
  return data;
}

export async function getRecipeByMenuItem(menuItemId) {
  const { data } = await apiClient.get(`/recipes/by-menu-item/${menuItemId}`);
  return data;
}

export async function createRecipe(payload) {
  const { data } = await apiClient.post('/recipes', payload);
  return data;
}

export async function updateRecipe(id, payload) {
  const { data } = await apiClient.put(`/recipes/${id}`, payload);
  return data;
}

export async function deleteRecipe(id) {
  const { data } = await apiClient.delete(`/recipes/${id}`);
  return data;
}
