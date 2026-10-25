import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

const TOKEN_KEY = 'dualwell_token';
const REFRESH_TOKEN_KEY = 'dualwell_refresh_token';

const AUTH_PATHS = ['/auth/login', '/auth/register', '/auth/refresh'];

// Interceptor to add Authorization Bearer token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

// Exchange the stored refresh token for a fresh access token. Uses plain
// axios so it never re-enters the response interceptor below.
let refreshPromise: Promise<string | null> | null = null;

const refreshAccessToken = async (): Promise<string | null> => {
  const stored = localStorage.getItem(REFRESH_TOKEN_KEY);
  if (!stored) return null;
  try {
    const res = await axios.post(`${API_BASE_URL}/auth/refresh`, {
      refresh_token: stored,
    });
    const { access_token, refresh_token } = res.data;
    localStorage.setItem(TOKEN_KEY, access_token);
    if (refresh_token) localStorage.setItem(REFRESH_TOKEN_KEY, refresh_token);
    return access_token;
  } catch {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    return null;
  }
};

const clearAuth = () => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

// Interceptor for 401 handling: silently renew the short-lived access token
// once, then replay the original request; log the user out if renewal fails.
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original: any = error.config;
    const status = error.response?.status;
    const isAuthCall = original?.url && AUTH_PATHS.some((p) => original.url.includes(p));

    if (status === 401 && original && !original._retry && !isAuthCall) {
      original._retry = true;
      if (!refreshPromise) {
        refreshPromise = refreshAccessToken().finally(() => {
          refreshPromise = null;
        });
      }
      const freshToken = await refreshPromise;
      if (freshToken) {
        original.headers = original.headers ?? {};
        original.headers.Authorization = `Bearer ${freshToken}`;
        return apiClient(original);
      }
    }

    if (status === 401) {
      // Refresh failed or this was an auth call: end the session.
      clearAuth();
      if (window.location.pathname !== '/login') {
        window.dispatchEvent(new Event('auth_expired'));
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;