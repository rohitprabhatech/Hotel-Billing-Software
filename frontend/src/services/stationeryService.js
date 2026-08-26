import apiClient from './apiClient';

export async function fetchStationeryPosCatalog(params = {}) {
  const { data } = await apiClient.get('/stationery/pos-catalog', { params });
  return data;
}

export async function searchStationeryProducts(params = {}) {
  const { data } = await apiClient.get('/stationery/products/search', { params });
  return data;
}

export async function getStationeryByBarcode(barcode, params = {}) {
  const { data } = await apiClient.get(
    `/stationery/products/by-barcode/${encodeURIComponent(barcode)}`,
    { params },
  );
  return data;
}
