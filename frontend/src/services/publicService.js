import apiClient from './apiClient';

export async function listPublicPlans() {
  const { data } = await apiClient.get('/public/plans');
  return data;
}
