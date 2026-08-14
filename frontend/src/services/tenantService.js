import apiClient from './apiClient';

export async function fetchMyTenant() {
  const { data } = await apiClient.get('/tenants/me');
  return data;
}

export async function updateMyTenant(payload) {
  const { data } = await apiClient.put('/tenants/me', payload);
  return data;
}

export async function fetchBusinessTypes() {
  const { data } = await apiClient.get('/tenants/business-types');
  return data;
}

export async function fetchWhatsappConfig() {
  const { data } = await apiClient.get('/tenants/me/whatsapp');
  return data;
}

export async function saveWhatsappConfig(payload) {
  const { data } = await apiClient.put('/tenants/me/whatsapp', payload);
  return data;
}

export async function testWhatsappConfig() {
  const { data } = await apiClient.post('/tenants/me/whatsapp/test');
  return data;
}

export async function disconnectWhatsappConfig() {
  const { data } = await apiClient.post('/tenants/me/whatsapp/disconnect');
  return data;
}

export async function simulateWhatsappDeliveryStatus(payload) {
  const { data } = await apiClient.post(
    '/tenants/me/whatsapp/simulate-delivery-status',
    payload,
  );
  return data;
}