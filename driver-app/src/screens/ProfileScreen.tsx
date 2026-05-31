import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { useAuth } from '../context/AuthContext';
import { apiRequest } from '../config';

export function ProfileScreen() {
  const { user: authUser, logout } = useAuth();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchProfile = () => {
    setLoading(true);
    setError('');
    apiRequest('/auth/me')
      .then(d => { setProfile(d); setLoading(false); })
      .catch(() => { setError('Failed to load profile'); setLoading(false); });
  };

  useEffect(() => { fetchProfile(); }, []);

  const u = profile || authUser;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Profile</Text>
      </View>

      <ScrollView contentContainerStyle={styles.screenContent}>
        {loading ? (
          <ActivityIndicator size="large" color={theme.colors.primary} style={{ marginVertical: 40 }} />
        ) : error ? (
          <View style={{ alignItems: 'center', paddingVertical: 32 }}>
            <Feather name="alert-circle" size={40} color={theme.colors.danger} />
            <Text style={{ color: theme.colors.textSecondary, marginTop: 12, marginBottom: 16 }}>{error}</Text>
            <TouchableOpacity onPress={fetchProfile} style={{ backgroundColor: theme.colors.primary, paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8 }}>
              <Text style={{ color: 'white', fontWeight: '600' }}>Retry</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <>
            <View style={styles.profileHeader}>
              <View style={styles.profileAvatar}>
                <Text style={styles.profileInitial}>{(u?.full_name || '').split(' ').map((s: string) => s[0]).join('')}</Text>
              </View>
              <Text style={styles.profileName}>{u?.full_name || ''}</Text>
              <Text style={styles.profileRole}>{u?.role ? u.role.charAt(0).toUpperCase() + u.role.slice(1) : ''}</Text>
            </View>

            <View style={styles.profileSection}>
              <Text style={styles.profileLabel}>Personal Info</Text>
              <View style={styles.profileInfoCard}>
                <View style={styles.profileInfoRow}>
                  <Text style={styles.profileInfoLabel}>Phone</Text>
                  <Text style={styles.profileInfoValue}>{u?.phone || ''}</Text>
                </View>
                <View style={styles.profileInfoRow}>
                  <Text style={styles.profileInfoLabel}>Email</Text>
                  <Text style={styles.profileInfoValue}>{u?.email || ''}</Text>
                </View>
                <View style={styles.profileInfoRow}>
                  <Text style={styles.profileInfoLabel}>License</Text>
                  <Text style={styles.profileInfoValue}>{u?.license || ''}</Text>
                </View>
              </View>
            </View>

            <View style={styles.profileSection}>
              <Text style={styles.profileLabel}>Assigned Vehicle</Text>
              <View style={styles.profileInfoCard}>
                <Text style={styles.profileInfoValue}>{u?.vehicle || ''}</Text>
              </View>
            </View>

            <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
              <Feather name="log-out" size={20} color={theme.colors.danger} />
              <Text style={styles.logoutBtnText}>Logout</Text>
            </TouchableOpacity>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
