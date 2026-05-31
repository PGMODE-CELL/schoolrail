import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import NetInfo from '@react-native-community/netinfo';
import { apiRequest } from '../config';

interface AuthState {
  user: any | null;
  token: string | null;
  isLoading: boolean;
  isOffline: boolean;
  login: (token: string, user: any) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (user: any) => Promise<void>;
}

export const AuthContext = createContext<AuthState>({
  user: null,
  token: null,
  isLoading: true,
  isOffline: false,
  login: async () => {},
  logout: async () => {},
  updateUser: async () => {},
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<any | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isOffline, setIsOffline] = useState(false);
  const unsubscribeRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    const init = async () => {
      const netState = await NetInfo.fetch();
      setIsOffline(!netState.isConnected);

      const storedToken = await AsyncStorage.getItem('token');
      const storedUser = await AsyncStorage.getItem('user');

      if (storedToken && storedUser) {
        setToken(storedToken);
        setUser(JSON.parse(storedUser));

        if (netState.isConnected) {
          try {
            const freshUser = await apiRequest('/auth/me');
            setUser(freshUser);
            await AsyncStorage.setItem('user', JSON.stringify(freshUser));
          } catch {
            const stored = await AsyncStorage.getItem('user');
            if (stored) setUser(JSON.parse(stored));
          }
        }
      }
      setIsLoading(false);
    };
    init();

    const unsub = NetInfo.addEventListener(state => {
      setIsOffline(!state.isConnected);
    });
    unsubscribeRef.current = unsub;

    return () => {
      if (unsubscribeRef.current) unsubscribeRef.current();
    };
  }, []);

  const login = useCallback(async (newToken: string, newUser: any) => {
    setToken(newToken);
    setUser(newUser);
    await AsyncStorage.setItem('token', newToken);
    await AsyncStorage.setItem('user', JSON.stringify(newUser));
  }, []);

  const logout = useCallback(async () => {
    setToken(null);
    setUser(null);
    await AsyncStorage.multiRemove(['token', 'user']);
  }, []);

  const updateUser = useCallback(async (updatedUser: any) => {
    setUser(updatedUser);
    await AsyncStorage.setItem('user', JSON.stringify(updatedUser));
  }, []);

  return (
    <AuthContext.Provider value={{ user, token, isLoading, isOffline, login, logout, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
}
