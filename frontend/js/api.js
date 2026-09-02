/**
 * NirikshanX API Client Module
 */
const API_BASE_URL = window.location.origin;

export function getToken() {
  return localStorage.getItem('nx_token') || '';
}

export function setToken(token) {
  if (token) {
    localStorage.setItem('nx_token', token);
  } else {
    localStorage.removeItem('nx_token');
  }
}

export async function apiFetch(endpoint, options = {}) {
  const token = getToken();
  const headers = options.headers || {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (!(options.body instanceof FormData) && !headers['Content-Type']) {
    headers['Content-Type'] = 'application/json';
  }

  const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const response = await fetch(`${API_BASE_URL}${cleanEndpoint}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    setToken(null);
    if (!window.location.pathname.endsWith('/') && !window.location.pathname.endsWith('index.html')) {
      window.location.href = '/';
    }
    throw new Error('Session expired or unauthorized');
  }

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(data.detail || `Request failed with status ${response.status}`);
  }
  return data;
}

export async function loginUser(username, password) {
  const data = await apiFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
  if (data.access_token) {
    setToken(data.access_token);
  }
  return data;
}

export async function registerUser(email, password, full_name, role = 'USER') {
  const data = await apiFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify({ email, password, full_name, role }),
  });
  if (data.access_token) {
    setToken(data.access_token);
  }
  return data;
}

export async function getCurrentUser() {
  return await apiFetch('/auth/me');
}
