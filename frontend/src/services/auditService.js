import apiClient from './apiClient';

export async function listAuditLogs(params = {}) {
  const { data } = await apiClient.get('/audit-logs', { params });
  return data;
}

export async function getAuditLog(id) {
  const { data } = await apiClient.get(`/audit-logs/${id}`);
  return data;
}

export async function fetchAuditAlerts() {
  const { data } = await apiClient.get('/audit-logs/alerts');
  return data;
}

export async function fetchAuditMeta() {
  const { data } = await apiClient.get('/audit-logs/meta');
  return data;
}

export async function deleteAuditLog(id) {
  const { data } = await apiClient.delete(`/audit-logs/${id}`);
  return data;
}