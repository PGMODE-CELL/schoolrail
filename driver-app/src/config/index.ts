import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { createSyncEngine } from '../sync/SyncEngine';

export const API_BASE = typeof window !== 'undefined'
  ? `${window.location.protocol}//${window.location.host}/api/v1`
  : 'http://10.0.2.2:3001/api/v1';

export async function apiRequest(endpoint: string, method: string = 'GET', body?: any): Promise<any> {
  const token = await AsyncStorage.getItem('token').catch(() => null);
  const config: RequestInit = {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  };
  if (body) config.body = JSON.stringify(body);
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

export async function isOnline(): Promise<boolean> {
  const state = await NetInfo.fetch();
  return state.isConnected ?? false;
}

export async function cachedFetch(url: string, options: RequestInit = {}, ttlSeconds: number = 300): Promise<any> {
  const cacheKey = `cache:${url}`;
  const cached = await AsyncStorage.getItem(cacheKey).catch(() => null);
  if (cached) {
    const { data, timestamp } = JSON.parse(cached);
    if (Date.now() - timestamp < ttlSeconds * 1000) {
      return data;
    }
  }
  const token = await AsyncStorage.getItem('token').catch(() => null);
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    },
  };
  const response = await fetch(`${API_BASE}${url}`, config);
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  const data = await response.json();
  await AsyncStorage.setItem(cacheKey, JSON.stringify({ data, timestamp: Date.now() }));
  return data;
}

export const syncEngine = createSyncEngine(apiRequest);
