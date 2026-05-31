import AsyncStorage from '@react-native-async-storage/async-storage';

export const API_BASE = typeof window !== 'undefined'
  ? `${window.location.protocol}//${window.location.host}/api/v1`
  : 'http://10.0.2.2:3001/api/v1';

export async function apiRequest(endpoint: string, options: RequestInit = {}): Promise<any> {
  const token = await AsyncStorage.getItem('token').catch(() => null);
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  };
  const response = await fetch(`${API_BASE}${endpoint}`, config);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

export async function apiLogin(username: string, password: string) {
  const formData = new URLSearchParams();
  formData.append('username', username);
  formData.append('password', password);
  const response = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString(),
  });
  if (!response.ok) throw new Error('Invalid credentials');
  return response.json();
}
