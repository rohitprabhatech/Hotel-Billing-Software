import axios from 'axios';

const apiClient = axios.create({
  baseURL:
    import.meta.env.VITE_API_BASE_URL ||
    (import.meta.env.DEV ? '/api/v1' : 'http://localhost:5003/api/v1'),
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type'];
  }
  return config;
});

const PUBLIC_AUTH_PATHS = [
  '/login',
  '/master/login',
  '/register',
  '/forgot-password',
  '/reset-password',
  '/verify-email',
];

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      const path = window.location.pathname;
      const hadSession = Boolean(localStorage.getItem('access_token'));
      localStorage.removeItem('access_token');
      localStorage.removeItem('auth_user');
      // Only force navigation away from protected pages when a session existed.
      if (hadSession && !PUBLIC_AUTH_PATHS.includes(path)) {
        const next = path.startsWith('/master') ? '/master/login' : '/login';
        window.location.assign(next);
      }
    }
    return Promise.reject(error);
  },
);

export default apiClient;
