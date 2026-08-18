import apiClient from './apiClient';

export async function fetchMasterDashboardSummary() {
  const { data } = await apiClient.get('/master/dashboard/summary');
  return data;
}

export async function listRegistrationRequests(params = {}) {
  const { data } = await apiClient.get('/master/registration-requests', { params });
  return data;
}

export async function getRegistrationRequest(id) {
  const { data } = await apiClient.get(`/master/registration-requests/${id}`);
  return data;
}

export async function approveRegistrationRequest(id) {
  const { data } = await apiClient.post(`/master/registration-requests/${id}/approve`);
  return data;
}

export async function rejectRegistrationRequest(id, reason) {
  const { data } = await apiClient.post(`/master/registration-requests/${id}/reject`, { reason });
  return data;
}

export async function fetchTrialSettings() {
  const { data } = await apiClient.get('/master/settings/trial');
  return data;
}

export async function updateTrialSettings(payload) {
  const { data } = await apiClient.put('/master/settings/trial', payload);
  return data;
}

export async function listMasterTrials(params = {}) {
  const { data } = await apiClient.get('/master/trials', { params });
  return data;
}

export async function listPlans(params = {}) {
  const { data } = await apiClient.get('/master/plans', { params });
  return data;
}

export async function getPlan(id) {
  const { data } = await apiClient.get(`/master/plans/${id}`);
  return data;
}

export async function createPlan(payload) {
  const { data } = await apiClient.post('/master/plans', payload);
  return data;
}

export async function updatePlan(id, payload) {
  const { data } = await apiClient.put(`/master/plans/${id}`, payload);
  return data;
}

export async function setPlanStatus(id, isActive) {
  const { data } = await apiClient.patch(`/master/plans/${id}/status`, { is_active: isActive });
  return data;
}

export async function listMasterBusinesses(params = {}) {
  const { data } = await apiClient.get('/master/businesses', { params });
  return data;
}

export async function listExpiringBusinesses(params = {}) {
  const { data } = await apiClient.get('/master/businesses/expiring', { params });
  return data;
}

export async function assignBusinessPlan(tenantId, payload) {
  const { data } = await apiClient.post(`/master/businesses/${tenantId}/assign-plan`, payload);
  return data;
}

export async function extendBusinessTrial(tenantId, days) {
  const { data } = await apiClient.post(`/master/businesses/${tenantId}/extend-trial`, { days });
  return data;
}

export async function renewBusinessSubscription(tenantId, payload) {
  const { data } = await apiClient.post(`/master/businesses/${tenantId}/renew`, payload);
  return data;
}

export async function cancelBusinessSubscription(tenantId) {
  const { data } = await apiClient.post(`/master/businesses/${tenantId}/cancel-subscription`);
  return data;
}

export async function listMasterNotifications(params = {}) {
  const { data } = await apiClient.get('/master/notifications', { params });
  return data;
}

export async function fetchMasterUnreadNotificationCount() {
  const { data } = await apiClient.get('/master/notifications/unread-count');
  return data;
}

export async function markMasterNotificationRead(id) {
  const { data } = await apiClient.patch(`/master/notifications/${id}/read`);
  return data;
}

export async function markAllMasterNotificationsRead() {
  const { data } = await apiClient.patch('/master/notifications/read-all');
  return data;
}

export async function runExpiryCheckJob() {
  const { data } = await apiClient.post('/master/jobs/expiry-check');
  return data;
}
