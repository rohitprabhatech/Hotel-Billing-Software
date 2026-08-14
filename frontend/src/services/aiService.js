import apiClient from './apiClient';

export async function fetchAiAnalysis(params = {}) {
  const { data } = await apiClient.get('/ai/analysis', { params });
  return data;
}

export async function fetchAiDecisions(params = {}) {
  const { data } = await apiClient.get('/ai/decisions', { params });
  return data;
}
