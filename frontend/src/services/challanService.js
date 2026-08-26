import apiClient from './apiClient';

export async function listChallans(params = {}) {
  const { data } = await apiClient.get('/challans', { params });
  return data;
}

export async function getChallan(challanId) {
  const { data } = await apiClient.get(`/challans/${challanId}`);
  return data;
}

export async function createChallan(payload) {
  const { data } = await apiClient.post('/challans', payload);
  return data;
}

export async function updateChallanStatus(challanId, payload) {
  const { data } = await apiClient.patch(`/challans/${challanId}/status`, payload);
  return data;
}

export async function convertChallan(challanId, payload = {}) {
  const { data } = await apiClient.post(`/challans/${challanId}/convert`, payload);
  return data;
}

export async function downloadChallanPdf(challanId, challanNumber) {
  const response = await apiClient.get(`/challans/${challanId}/pdf`, {
    responseType: 'blob',
  });
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', `${challanNumber || 'challan'}.pdf`);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
