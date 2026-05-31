/**
 * SchoolRail - Custom React Hooks
 */

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI, schoolsAPI, vehiclesAPI, driversAPI, routesAPI, studentsAPI, attendanceAPI, feesAPI, alertsAPI, tripsAPI } from '@/lib/api';

// Types
interface User {
  id: number;
  username: string;
  email: string;
  name: string;
  role: string;
  school_id: number | null;
}

interface AuthState {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
}

// =============================================================================
// Auth Hook
// =============================================================================

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isLoading: true,
    isAuthenticated: false,
  });
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('token');
      const userStr = localStorage.getItem('user');

      if (token && userStr) {
        const user = JSON.parse(userStr);
        setState({
          user,
          isLoading: false,
          isAuthenticated: true,
        });
      } else {
        setState({
          user: null,
          isLoading: false,
          isAuthenticated: false,
        });
        router.push('/');
      }
    } catch (error) {
      setState({
        user: null,
        isLoading: false,
        isAuthenticated: false,
      });
      router.push('/');
    }
  };

  const login = async (username: string, password: string) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const { data } = await authAPI.login({ username, password });
      
      localStorage.setItem('token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));
      
      setState({
        user: data.user,
        isLoading: false,
        isAuthenticated: true,
      });
      
      router.push('/dashboard');
      return { success: true };
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Login failed' 
      };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setState({
      user: null,
      isLoading: false,
      isAuthenticated: false,
    });
    router.push('/');
  };

  return {
    ...state,
    login,
    logout,
  };
}

// =============================================================================
// Fetch Hook with Caching
// =============================================================================

interface FetchState<T> {
  data: T | null;
  isLoading: boolean;
  error: string | null;
}

export function useFetch<T>(
  fetchFn: () => Promise<any>,
  dependencies: any[] = [],
  options?: {
    immediate?: boolean;
    cache?: boolean;
  }
) {
  const [state, setState] = useState<FetchState<T>>({
    data: null,
    isLoading: options?.immediate ?? true,
    error: null,
  });

  const cacheRef = useRef<Map<string, T>>(new Map());

  const execute = useCallback(async () => {
    setState(prev => ({ ...prev, isLoading: true, error: null }));
    
    try {
      const cacheKey = JSON.stringify(dependencies);
      
      if (options?.cache && cacheRef.current.has(cacheKey)) {
        setState({
          data: cacheRef.current.get(cacheKey) as T,
          isLoading: false,
          error: null,
        });
        return;
      }

      const response = await fetchFn();
      const data = response.data;

      if (options?.cache) {
        cacheRef.current.set(cacheKey, data);
      }

      setState({
        data,
        isLoading: false,
        error: null,
      });
    } catch (error: any) {
      setState({
        data: null,
        isLoading: false,
        error: error.response?.data?.message || 'An error occurred',
      });
    }
  }, dependencies);

  useEffect(() => {
    if (options?.immediate !== false) {
      execute();
    }
  }, [execute]);

  return {
    ...state,
    refetch: execute,
  };
}

// =============================================================================
// Schools Hook
// =============================================================================

export function useSchools(params?: any) {
  return useFetch(() => schoolsAPI.list(params), [params]);
}

export function useSchool(id: number) {
  return useFetch(() => schoolsAPI.get(id), [id], { immediate: !!id });
}

// =============================================================================
// Vehicles Hook
// =============================================================================

export function useVehicles(params?: any) {
  return useFetch(() => vehiclesAPI.list(params), [params]);
}

export function useVehicle(id: number) {
  return useFetch(() => vehiclesAPI.get(id), [id], { immediate: !!id });
}

export function useVehicleLocation(id: number) {
  return useFetch(() => vehiclesAPI.location(id), [id], { 
    immediate: !!id,
    cache: true 
  });
}

// =============================================================================
// Drivers Hook
// =============================================================================

export function useDrivers(params?: any) {
  return useFetch(() => driversAPI.list(params), [params]);
}

export function useDriver(id: number) {
  return useFetch(() => driversAPI.get(id), [id], { immediate: !!id });
}

// =============================================================================
// Routes Hook
// =============================================================================

export function useRoutes(params?: any) {
  return useFetch(() => routesAPI.list(params), [params]);
}

export function useRoute(id: number) {
  return useFetch(() => routesAPI.get(id), [id], { immediate: !!id });
}

// =============================================================================
// Students Hook
// =============================================================================

export function useStudents(params?: any) {
  return useFetch(() => studentsAPI.list(params), [params]);
}

export function useStudent(id: number) {
  return useFetch(() => studentsAPI.get(id), [id], { immediate: !!id });
}

// =============================================================================
// Attendance Hook
// =============================================================================

export function useAttendance(params?: any) {
  return useFetch(() => attendanceAPI.list(params), [params]);
}

export function useDailyAttendance(params?: any) {
  return useFetch(() => attendanceAPI.daily(params), [params], {
    immediate: true,
    cache: true,
  });
}

// =============================================================================
// Fees Hook
// =============================================================================

export function useFees(params?: any) {
  return useFetch(() => feesAPI.list(params), [params]);
}

export function useFee(id: number) {
  return useFetch(() => feesAPI.get(id), [id], { immediate: !!id });
}

// =============================================================================
// Alerts Hook
// =============================================================================

export function useAlerts(params?: any) {
  return useFetch(() => alertsAPI.list(params), [params]);
}

export function useUnreadAlerts() {
  return useFetch(() => alertsAPI.list({ unread_only: true }), [], {
    immediate: true,
    cache: true,
  });
}

// =============================================================================
// Trips Hook
// =============================================================================

export function useTrips(params?: any) {
  return useFetch(() => tripsAPI.list(params), [params]);
}

export function useTrip(id: number) {
  return useFetch(() => tripsAPI.get(id), [id], { immediate: !!id });
}

// =============================================================================
// Pagination Hook
// =============================================================================

interface PaginationState {
  page: number;
  limit: number;
  total: number;
}

export function usePagination(initialPage = 1, initialLimit = 20) {
  const [state, setState] = useState<PaginationState>({
    page: initialPage,
    limit: initialLimit,
    total: 0,
  });

  const setPage = (page: number) => setState(prev => ({ ...prev, page }));
  const setLimit = (limit: number) => setState(prev => ({ ...prev, limit, page: 1 }));
  const setTotal = (total: number) => setState(prev => ({ ...prev, total }));

  const totalPages = Math.ceil(state.total / state.limit);
  const offset = (state.page - 1) * state.limit;

  return {
    ...state,
    setPage,
    setLimit,
    setTotal,
    totalPages,
    offset,
    hasNextPage: state.page < totalPages,
    hasPrevPage: state.page > 1,
  };
}

// =============================================================================
// Search Hook
// =============================================================================

export function useSearch(initialValue = '', delay = 500) {
  const [value, setValue] = useState(initialValue);
  const [debouncedValue, setDebouncedValue] = useState(initialValue);
  const timeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [value, delay]);

  return {
    value,
    setValue,
    debouncedValue,
  };
}

// =============================================================================
// Form Hook
// =============================================================================

interface FormState<T> {
  values: T;
  errors: Partial<Record<keyof T, string>>;
  isSubmitting: boolean;
  isDirty: boolean;
}

export function useForm<T extends Record<string, any>>(initialValues: T) {
  const [state, setState] = useState<FormState<T>>({
    values: initialValues,
    errors: {},
    isSubmitting: false,
    isDirty: false,
  });

  const setFieldValue = (field: keyof T, value: any) => {
    setState(prev => ({
      ...prev,
      values: { ...prev.values, [field]: value },
      isDirty: true,
    }));
  };

  const setFieldError = (field: keyof T, error: string) => {
    setState(prev => ({
      ...prev,
      errors: { ...prev.errors, [field]: error },
    }));
  };

  const reset = () => {
    setState({
      values: initialValues,
      errors: {},
      isSubmitting: false,
      isDirty: false,
    });
  };

  const handleSubmit = async (onSubmit: (values: T) => Promise<any>) => {
    setState(prev => ({ ...prev, isSubmitting: true }));
    try {
      await onSubmit(state.values);
      setState(prev => ({ ...prev, isSubmitting: false }));
    } catch (error: any) {
      if (error.response?.data) {
        const errors: any = {};
        Object.entries(error.response.data).forEach(([key, value]: [string, any]) => {
          errors[key] = Array.isArray(value) ? value[0] : value;
        });
        setState(prev => ({ ...prev, errors, isSubmitting: false }));
      } else {
        setState(prev => ({ ...prev, isSubmitting: false }));
      }
    }
  };

  return {
    ...state,
    setFieldValue,
    setFieldError,
    reset,
    handleSubmit,
  };
}

// =============================================================================
// Local Storage Hook
// =============================================================================

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === 'undefined') return initialValue;
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch (error) {
      return initialValue;
    }
  });

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value;
      setStoredValue(valueToStore);
      if (typeof window !== 'undefined') {
        window.localStorage.setItem(key, JSON.stringify(valueToStore));
      }
    } catch (error) {
      console.error('Error saving to localStorage:', error);
    }
  };

  return [storedValue, setValue] as const;
}

// =============================================================================
// Interval Hook
// =============================================================================

export function useInterval(callback: () => void, delay: number | null) {
  const savedCallback = useRef(callback);

  useEffect(() => {
    savedCallback.current = callback;
  }, [callback]);

  useEffect(() => {
    if (delay === null) return;

    const id = setInterval(() => savedCallback.current(), delay);
    return () => clearInterval(id);
  }, [delay]);
}

// =============================================================================
// Toggle Hook
// =============================================================================

export function useToggle(initialValue = false): [boolean, () => void] {
  const [value, setValue] = useState(initialValue);
  const toggle = useCallback(() => setValue(v => !v), []);
  return [value, toggle];
}

// =============================================================================
// Sidebar Hook
// =============================================================================

export function useSidebar() {
  const [isOpen, setIsOpen] = useState(false);
  const [isMobile, setIsMobile] = useState(false);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 1024);
    };
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen(v => !v), []);

  return {
    isOpen,
    isMobile,
    open,
    close,
    toggle,
  };
}

// Export all hooks
export default {
  useAuth,
  useFetch,
  useSchools,
  useSchool,
  useVehicles,
  useVehicle,
  useVehicleLocation,
  useDrivers,
  useDriver,
  useRoutes,
  useRoute,
  useStudents,
  useStudent,
  useAttendance,
  useDailyAttendance,
  useFees,
  useFee,
  useAlerts,
  useUnreadAlerts,
  usePagination,
  useSearch,
  useForm,
  useLocalStorage,
  useInterval,
  useToggle,
  useSidebar,
};