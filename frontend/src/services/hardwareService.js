import apiClient from './apiClient';

export async function fetchHardwarePosCatalog(params = {}) {
  const { data } = await apiClient.get('/hardware/pos-catalog', { params });
  return data;
}

export async function fetchHardwareUnits() {
  const { data } = await apiClient.get('/hardware/units');
  return data;
}

export async function quoteHardwareLine(payload) {
  const { data } = await apiClient.post('/hardware/quote', payload);
  return data;
}

export async function convertHardwareQuantity(payload) {
  const { data } = await apiClient.post('/hardware/convert', payload);
  return data;
}
