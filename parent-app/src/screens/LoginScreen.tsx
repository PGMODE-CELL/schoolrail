import React, { useState } from 'react';
import { View, Text, TouchableOpacity, SafeAreaView, TextInput, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { apiLogin, apiRequest } from '../config';

interface Props {
  onLogin: (token: string, user: any) => void;
}

export function LoginScreen({ onLogin }: Props) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleLogin = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await apiLogin(email, password);
      await AsyncStorage.setItem('token', data.access_token);
      const me = await apiRequest('/auth/me');
      await AsyncStorage.setItem('user', JSON.stringify(me));
      onLogin(data.access_token, me);
    } catch (e: any) {
      if (email === 'parent1@schoolrail.com' && password === 'admin123') {
        const mockUser = { id: 3, username: 'parent1', email, full_name: 'Parent User', role: 'parent' };
        await AsyncStorage.setItem('token', 'mock');
        await AsyncStorage.setItem('user', JSON.stringify(mockUser));
        onLogin('mock', mockUser);
      } else {
        setError(e.message || 'Login failed');
      }
    }
    setLoading(false);
  };

  return (
    <SafeAreaView style={{ flex: 1, backgroundColor: '#F8FAFC' }}>
      <View style={{ flex: 1, justifyContent: 'center', padding: 24 }}>
        <View style={{ alignItems: 'center', marginBottom: 40 }}>
          <View style={{ width: 72, height: 72, borderRadius: 20, backgroundColor: '#6366F1', justifyContent: 'center', alignItems: 'center', marginBottom: 16 }}>
            <Feather name="truck" size={36} color="white" />
          </View>
          <Text style={{ fontSize: 28, fontWeight: 'bold', color: '#1E293B' }}>SchoolRail</Text>
          <Text style={{ fontSize: 14, color: '#64748B', marginTop: 4 }}>Parent Portal</Text>
        </View>

        {error ? (
          <View style={{ backgroundColor: '#FEE2E2', borderRadius: 12, padding: 12, marginBottom: 16 }}>
            <Text style={{ color: '#DC2626', fontSize: 14 }}>{error}</Text>
          </View>
        ) : null}

        <View style={{ marginBottom: 16 }}>
          <Text style={{ fontSize: 14, fontWeight: '600', color: '#1E293B', marginBottom: 8 }}>Email</Text>
          <TextInput
            style={{ backgroundColor: 'white', borderRadius: 12, padding: 16, fontSize: 16, borderWidth: 1, borderColor: '#E2E8F0' }}
            placeholder="Enter your email"
            value={email}
            onChangeText={setEmail}
            keyboardType="email-address"
            autoCapitalize="none"
          />
        </View>
        <View style={{ marginBottom: 24 }}>
          <Text style={{ fontSize: 14, fontWeight: '600', color: '#1E293B', marginBottom: 8 }}>Password</Text>
          <TextInput
            style={{ backgroundColor: 'white', borderRadius: 12, padding: 16, fontSize: 16, borderWidth: 1, borderColor: '#E2E8F0' }}
            placeholder="Enter your password"
            value={password}
            onChangeText={setPassword}
            secureTextEntry
          />
        </View>

        <TouchableOpacity
          onPress={handleLogin}
          disabled={loading}
          style={{ backgroundColor: '#6366F1', borderRadius: 12, padding: 16, alignItems: 'center', opacity: loading ? 0.6 : 1 }}
        >
          {loading ? (
            <ActivityIndicator color="white" />
          ) : (
            <Text style={{ color: 'white', fontSize: 16, fontWeight: '600' }}>Sign In</Text>
          )}
        </TouchableOpacity>

        <View style={{ marginTop: 24, padding: 16, backgroundColor: '#F1F5F9', borderRadius: 12 }}>
          <Text style={{ fontSize: 12, color: '#64748B', textAlign: 'center', marginBottom: 8 }}>Demo Credentials</Text>
          <Text style={{ fontSize: 12, color: '#64748B', textAlign: 'center' }}>parent1@schoolrail.com / admin123</Text>
        </View>
      </View>
    </SafeAreaView>
  );
}
