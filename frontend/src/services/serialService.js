import apiClient from './apiClient';

export async function listSerialUnits(params = {}) {
  const { data } = await apiClient.get('/serial-units', { params });
  return data;
}

export async function getSerialUnitBySerial(serial) {
  const { data } = await apiClient.get(`/serial-units/by-serial/${encodeURIComponent(serial)}`);
  return data;
}

export async function receiveSerialUnit(payload) {
  const { data } = await apiClient.post('/serial-units', payload);
  return data;
}
