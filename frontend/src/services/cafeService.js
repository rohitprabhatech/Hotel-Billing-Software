import apiClient from './apiClient';

export async function fetchPosCatalog() {
  const { data } = await apiClient.get('/cafe/pos-catalog');
  return data;
}

export async function fetchCafeDashboard(params = {}) {
  const { data } = await apiClient.get('/cafe/dashboard', { params });
  return data;
}

export async function listCombos(params = {}) {
  const { data } = await apiClient.get('/combos', { params });
  return data;
}

export async function createCombo(payload) {
  const { data } = await apiClient.post('/combos', payload);
  return data;
}

export async function deleteCombo(id) {
  const { data } = await apiClient.delete(`/combos/${id}`);
  return data;
}

export async function listAddonGroups() {
  const { data } = await apiClient.get('/menu/addons');
  return data;
}

export async function createAddonGroup(payload) {
  const { data } = await apiClient.post('/menu/addons', payload);
  return data;
}

export async function deleteAddonGroup(id) {
  const { data } = await apiClient.delete(`/menu/addons/${id}`);
  return data;
}
