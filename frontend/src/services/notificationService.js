import apiClient from './apiClient';

export async function listNotifications(params = {}) {
  const { data } = await apiClient.get('/notifications', { params });
  return data;
}

export async function fetchUnreadNotificationCount() {
  const { data } = await apiClient.get('/notifications/unread-count');
  return data;
}

export async function markNotificationRead(id) {
  const { data } = await apiClient.patch(`/notifications/${id}/read`);
  return data;
}

export async function markAllNotificationsRead() {
  const { data } = await apiClient.patch('/notifications/read-all');
  return data;
}
