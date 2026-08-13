import apiClient from './apiClient';

export async function loginRequest(email, password) {
  const { data } = await apiClient.post('/auth/login', { email, password });
  return data;
}

export async function logoutRequest() {
  const { data } = await apiClient.post('/auth/logout');
  return data;
}

export async function fetchMe() {
  const { data } = await apiClient.get('/auth/me');
  return data;
}

export async function registerHotelRequest(payload) {
  const { data } = await apiClient.post('/auth/register-hotel', payload);
  return data;
}

export async function verifyEmailRequest(token) {
  const { data } = await apiClient.post('/auth/verify-email', { token });
  return data;
}

export async function resendVerificationRequest(email) {
  const { data } = await apiClient.post('/auth/resend-verification', { email });
  return data;
}

export async function forgotPasswordRequest(email) {
  const { data } = await apiClient.post('/auth/forgot-password', { email });
  return data;
}

export async function resetPasswordRequest(payload) {
  const { data } = await apiClient.post('/auth/reset-password', payload);
  return data;
}

export async function changePasswordRequest(payload) {
  const { data } = await apiClient.post('/auth/change-password', payload);
  return data;
}

export async function fetchProfile() {
  const { data } = await apiClient.get('/profile');
  return data;
}

export async function updateProfileRequest(payload) {
  const { data } = await apiClient.put('/profile', payload);
  return data;
}

export async function requestEmailChange(payload) {
  const { data } = await apiClient.post('/profile/request-email-change', payload);
  return data;
}
