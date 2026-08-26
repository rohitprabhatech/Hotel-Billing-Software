import apiClient from './apiClient';

export async function listTravelBookings(params = {}) {
  const { data } = await apiClient.get('/travel/bookings', { params });
  return data;
}

export async function getTravelBooking(bookingId) {
  const { data } = await apiClient.get(`/travel/bookings/${bookingId}`);
  return data;
}

export async function createTravelBooking(payload) {
  const { data } = await apiClient.post('/travel/bookings', payload);
  return data;
}

export async function updateTravelBookingStatus(bookingId, status) {
  const { data } = await apiClient.patch(`/travel/bookings/${bookingId}/status`, { status });
  return data;
}

export async function recordTravelBookingPayment(bookingId, payload) {
  const { data } = await apiClient.post(`/travel/bookings/${bookingId}/payments`, payload);
  return data;
}

export async function listTravelItinerary(bookingId) {
  const { data } = await apiClient.get(`/travel/bookings/${bookingId}/itinerary`);
  return data;
}

export async function createTravelItineraryItem(bookingId, payload) {
  const { data } = await apiClient.post(`/travel/bookings/${bookingId}/itinerary`, payload);
  return data;
}

export async function updateTravelItineraryItem(bookingId, itemId, payload) {
  const { data } = await apiClient.patch(
    `/travel/bookings/${bookingId}/itinerary/${itemId}`,
    payload,
  );
  return data;
}

export async function deleteTravelItineraryItem(bookingId, itemId) {
  const { data } = await apiClient.delete(`/travel/bookings/${bookingId}/itinerary/${itemId}`);
  return data;
}

export async function listTravelDocuments(bookingId) {
  const { data } = await apiClient.get(`/travel/bookings/${bookingId}/documents`);
  return data;
}

export async function createTravelDocument(bookingId, payload) {
  const { data } = await apiClient.post(`/travel/bookings/${bookingId}/documents`, payload);
  return data;
}

export async function deleteTravelDocument(bookingId, documentId) {
  const { data } = await apiClient.delete(
    `/travel/bookings/${bookingId}/documents/${documentId}`,
  );
  return data;
}
