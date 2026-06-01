import React, { useState } from 'react';
import { View, Text, TouchableOpacity, SafeAreaView, TextInput, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiLogin, apiRequest } from '../config';
import { useAuth } from '../context/AuthContext';

export function LoginScreen() {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});

  const validate = (): boolean => {
    const errs: { email?: string; password?: string } = {};
    if (!email.trim()) errs.email = 'Email is required';
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) errs.email = 'Invalid email format';
    if (!password) errs.password = 'Password is required';
    setFieldErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleLogin = async () => {
    setError('');
    if (!validate()) return;
    setLoading(true);
    try {
      const data = await apiLogin(email.trim(), password);
      await AsyncStorage.setItem('token', data.access_token);
      const me = await apiRequest('/auth/me');
      await AsyncStorage.setItem('user', JSON.stringify(me));
      await login(data.access_token, me);
    } catch (e: any) {
      setError(e.message || 'Login failed');
    }
    setLoading(false);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#F8FAFC' }}>
      <View style={{ flex: 1, justifyContent: 'center', padding: 24 }}>
        <View style={{ alignItems: 'center', marginBottom: 40 }}>
          <View style={{ width: 72, height: 72, borderRadius: 20, backgroundColor: '#10B981', justifyContent: 'center', alignItems: 'center', marginBottom: 16 }}>
            <Feather name="truck" size={36} color="white" />
          </View>
          <Text style={{ fontSize: 28, fontWeight: 'bold', color: '#1E293B' }}>SchoolRail</Text>
          <Text style={{ fontSize: 14, color: '#64748B', marginTop: 4 }}>Driver Portal</Text>
        </View>
        {error ? (
          <View style={{ backgroundColor: '#FEE2E2', borderRadius: 12, padding: 12, marginBottom: 16 }}>
            <Text style={{ color: '#DC2626', fontSize: 14 }}>{error}</Text>
          </View>
        ) : null}
        <View style={{ marginBottom: 16 }}>
          <Text style={{ fontSize: 14, fontWeight: '600', color: '#1E293B', marginBottom: 8 }}>Email</Text>
          <TextInput
            style={{ backgroundColor: 'white', borderRadius: 12, padding: 16, fontSize: 16, borderWidth: 1, borderColor: fieldErrors.email ? '#EF4444' : '#E2E8F0' }}
            placeholder="you@school.edu"
            value={email}
            onChangeText={(t) => { setEmail(t); setFieldErrors(p => ({ ...p, email: undefined })); }}
            keyboardType="email-address"
            autoCapitalize="none"
          />
          {fieldErrors.email ? (
            <Text style={{ color: '#EF4444', fontSize: 12, marginTop: 4 }}>{fieldErrors.email}</Text>
          ) : null}
        </View>
        <View style={{ marginBottom: 24 }}>
          <Text style={{ fontSize: 14, fontWeight: '600', color: '#1E293B', marginBottom: 8 }}>Password</Text>
          <TextInput
            style={{ backgroundColor: 'white', borderRadius: 12, padding: 16, fontSize: 16, borderWidth: 1, borderColor: fieldErrors.password ? '#EF4444' : '#E2E8F0' }}
            placeholder="Enter your password"
            value={password}
            onChangeText={(t) => { setPassword(t); setFieldErrors(p => ({ ...p, password: undefined })); }}
            secureTextEntry
          />
          {fieldErrors.password ? (
            <Text style={{ color: '#EF4444', fontSize: 12, marginTop: 4 }}>{fieldErrors.password}</Text>
          ) : null}
        </View>
        <TouchableOpacity
          onPress={handleLogin}
          disabled={loading}
          style={{ backgroundColor: '#10B981', borderRadius: 12, padding: 16, alignItems: 'center', opacity: loading ? 0.6 : 1 }}
        >
          {loading ? <ActivityIndicator color="white" /> : <Text style={{ color: 'white', fontSize: 16, fontWeight: '600' }}>Sign In</Text>}
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}
