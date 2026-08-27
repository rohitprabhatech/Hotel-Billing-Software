import apiClient from './apiClient';

export async function listTables(params = {}) {
  const { data } = await apiClient.get('/tables', { params });
  return data;
}

export async function createTable(payload) {
  const { data } = await apiClient.post('/tables', payload);
  return data;
}

export async function updateTable(id, payload) {
  const { data } = await apiClient.patch(`/tables/${id}`, payload);
  return data;
}

export async function deactivateTable(id) {
  const { data } = await apiClient.delete(`/tables/${id}`);
  return data;
}

export async function setTableStatus(id, status) {
  const { data } = await apiClient.post(`/tables/${id}/status`, { status });
  return data;
}

export async function listTableBills(tableId, params = {}) {
  const { data } = await apiClient.get(`/tables/${tableId}/bills`, { params });
  return data;
}

export async function mergeTables(payload) {
  const { data } = await apiClient.post('/tables/merge', payload);
  return data;
}

export async function unmergeTables(payload) {
  const { data } = await apiClient.post('/tables/unmerge', payload);
  return data;
}
