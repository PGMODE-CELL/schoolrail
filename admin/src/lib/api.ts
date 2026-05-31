/**
 * SchoolRail - Admin API Service
 * Centralized API service for all admin operations
 */

import axios from 'axios';

export interface Trip {
  id: number;
  school_id: number;
  vehicle_id: number;
  driver_id: number | null;
  route_id: number;
  trip_type: string;
  status: string;
  scheduled_start_time: string;
  scheduled_end_time: string | null;
  actual_start_time: string | null;
  actual_end_time: string | null;
  students_count: number;
  notes: string | null;
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3001/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  login: (credentials: { username: string; password: string }) =>
    api.post('/auth/login', new URLSearchParams(credentials)),
  
  register: (userData: any) => api.post('/auth/register', userData),
  
  me: () => api.get('/auth/me'),
  
  update: (data: any) => api.put('/auth/me', data),
  
  logout: () => api.post('/auth/logout'),
};

// Schools API
export const schoolsAPI = {
  list: (params?: any) => api.get('/schools', { params }),
  
  get: (id: number) => api.get(`/schools/${id}`),
  
  create: (data: any) => api.post('/schools', data),
  
  update: (id: number, data: any) => api.put(`/schools/${id}`, data),
  
  delete: (id: number) => api.delete(`/schools/${id}`),
  
  stats: (id: number) => api.get(`/schools/${id}/stats`),
};

// Vehicles API
export const vehiclesAPI = {
  list: (params?: any) => api.get('/vehicles', { params }),
  
  get: (id: number) => api.get(`/vehicles/${id}`),
  
  create: (data: any) => api.post('/vehicles', data),
  
  update: (id: number, data: any) => api.put(`/vehicles/${id}`, data),
  
  delete: (id: number) => api.delete(`/vehicles/${id}`),
  
  location: (id: number) => api.get(`/gps/vehicle/${id}`),
  
  history: (id: number, params?: any) => api.get(`/gps/vehicle/${id}/history`, { params }),
  
  maintenance: (id: number) => api.get(`/vehicles/${id}/maintenance`),
};

// Drivers API
export const driversAPI = {
  list: (params?: any) => api.get('/drivers', { params }),
  
  get: (id: number) => api.get(`/drivers/${id}`),
  
  create: (data: any) => api.post('/drivers', data),
  
  update: (id: number, data: any) => api.put(`/drivers/${id}`, data),
  
  delete: (id: number) => api.delete(`/drivers/${id}`),
  
  attendance: (id: number, params?: any) => api.get(`/drivers/${id}/attendance`, { params }),
};

// Routes API
export const routesAPI = {
  list: (params?: any) => api.get('/routes', { params }),
  
  get: (id: number) => api.get(`/routes/${id}`),
  
  create: (data: any) => api.post('/routes', data),
  
  update: (id: number, data: any) => api.put(`/routes/${id}`, data),
  
  delete: (id: number) => api.delete(`/routes/${id}`),
};

// Students API
export const studentsAPI = {
  list: (params?: any) => api.get('/students', { params }),
  
  get: (id: number) => api.get(`/students/${id}`),
  
  create: (data: any) => api.post('/students', data),
  
  update: (id: number, data: any) => api.put(`/students/${id}`, data),
  
  delete: (id: number) => api.delete(`/students/${id}`),
};

// Attendance API
export const attendanceAPI = {
  list: (params?: any) => api.get('/attendance/daily', {
    params: { attendance_date: params?.date || params?.attendance_date }
  }),

  create: (data: any) => api.post('/attendance', data),

  bulk: (data: any) => api.post('/attendance/bulk', data),

  daily: (params?: any) => api.get('/attendance/daily', {
    params: { attendance_date: params?.date || params?.attendance_date }
  }),
};

// Fees API
export const feesAPI = {
  list: (params?: any) => api.get('/fees', { params }),
  
  get: (id: number) => api.get(`/fees/${id}`),
  
  create: (data: any) => api.post('/fees', data),
  
  pay: (id: number, data: any) => api.post(`/fees/${id}/pay`, data),
};

// Trips API
export const tripsAPI = {
  list: (params?: any) => api.get('/trips', { params }),

  get: (id: number) => api.get(`/trips/${id}`),

  create: (data: any) => api.post('/trips', data),

  start: (id: number) => api.post(`/trips/${id}/start`),

  complete: (id: number, data?: any) => api.post(`/trips/${id}/complete`, data),
};

// GPS API
export const gpsAPI = {
  add: (data: any) => api.post('/gps/location', data),
  
  latest: (params?: any) => api.get('/gps/active', { params }),
};

// Alerts API
export const alertsAPI = {
  list: (params?: any) => api.get('/alerts', { params }),
  
  get: (id: number) => api.get(`/alerts/${id}`),
  
  markRead: (id: number) => api.post(`/alerts/${id}/read`),
  
  resolve: (id: number, data: any) => api.post(`/alerts/${id}/resolve`, data),
};

export default api;