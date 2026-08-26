import apiClient from './apiClient';

export async function fetchAvailableReports() {
  const { data } = await apiClient.get('/reports/available');
  return data;
}

export async function fetchReportSummary(params = {}) {
  const { data } = await apiClient.get('/reports/summary', { params });
  return data;
}

export async function fetchDailySales(params = {}) {
  const { data } = await apiClient.get('/reports/daily-sales', { params });
  return data;
}

export async function fetchWeeklySales(params = {}) {
  const { data } = await apiClient.get('/reports/weekly-sales', { params });
  return data;
}

export async function fetchMonthlySales(params = {}) {
  const { data } = await apiClient.get('/reports/monthly-sales', { params });
  return data;
}

export async function fetchCustomSales(params = {}) {
  const { data } = await apiClient.get('/reports/custom-sales', { params });
  return data;
}

export async function fetchFbReport(params = {}) {
  const { data } = await apiClient.get('/reports/fb', { params });
  return data;
}

export async function fetchOutstandingReport(params = {}) {
  const { data } = await apiClient.get('/reports/outstanding', { params });
  return data;
}

export function exportReportUrl(params = {}) {
  const search = new URLSearchParams(params);
  const base = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api/v1';
  return `${base}/reports/export?${search.toString()}`;
}

export async function downloadReport(params = {}) {
  const response = await apiClient.get('/reports/export', {
    params,
    responseType: 'blob',
  });
  const disposition = response.headers['content-disposition'] || '';
  const match = disposition.match(/filename="?([^"]+)"?/);
  const filename = match?.[1] || `sales_export.${params.format || 'xlsx'}`;
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}