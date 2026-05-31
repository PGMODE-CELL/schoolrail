import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';
import { useAuth } from '../context/AuthContext';

export function ProfileScreen() {
  const { user, logout } = useAuth();
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchStudents = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const d = await apiRequest('/students/');
      if (Array.isArray(d)) setStudents(d);
    } catch (e: any) {
      setError(e.message || 'Failed to fetch students');
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchStudents(); }, [fetchStudents]);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.screenHeader}>
          <Text style={styles.screenTitle}>Profile</Text>
        </View>
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.screenHeader}>
          <Text style={styles.screenTitle}>Profile</Text>
        </View>
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
          <Feather name="alert-circle" size={48} color={theme.colors.danger} />
          <Text style={{ fontSize: 16, color: theme.colors.textSecondary, marginTop: 16, textAlign: 'center' }}>{error}</Text>
          <TouchableOpacity
            onPress={fetchStudents}
            style={{ marginTop: 16, backgroundColor: theme.colors.primary, borderRadius: 12, paddingHorizontal: 24, paddingVertical: 12 }}
          >
            <Text style={{ color: 'white', fontSize: 14, fontWeight: '600' }}>Retry</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const displayChildren = students.map((s: any) => ({
    id: String(s.id),
    name: s.full_name || `${s.first_name} ${s.last_name}`,
    class: s.class_name || '',
    route: s.route_name || '',
    vehicle: s.vehicle_name || '',
  }));

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Profile</Text>
      </View>
      <ScrollView contentContainerStyle={styles.screenContent}>
        <View style={styles.profileHeader}>
          <View style={styles.profileAvatar}>
            <Text style={styles.profileInitial}>{(user?.full_name || 'U')[0]}</Text>
          </View>
          <Text style={styles.profileName}>{user?.full_name || ''}</Text>
          <Text style={styles.profileEmail}>{user?.email || ''}</Text>
        </View>

        <View style={styles.profileSection}>
          <Text style={styles.sectionTitle}>Personal Information</Text>
          <View style={styles.profileInfo}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Phone</Text>
              <Text style={styles.infoValue}>{user?.phone || ''}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Email</Text>
              <Text style={styles.infoValue}>{user?.email || ''}</Text>
            </View>
          </View>
        </View>

        {displayChildren.length > 0 && (
          <View style={styles.profileSection}>
            <Text style={styles.sectionTitle}>Children</Text>
            {displayChildren.map((child: any) => (
              <View key={child.id} style={styles.childInfoCard}>
                <View style={styles.childInfoAvatar}>
                  <Text style={styles.childInfoInitial}>{child.name[0]}</Text>
                </View>
                <View style={styles.childInfoDetails}>
                  <Text style={styles.childInfoName}>{child.name}</Text>
                  <Text style={styles.childInfoClass}>{child.class}</Text>
                  {(child.route || child.vehicle) && (
                    <Text style={styles.childInfoRoute}>{child.route} • {child.vehicle}</Text>
                  )}
                </View>
              </View>
            ))}
          </View>
        )}

        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Feather name="log-out" size={20} color={theme.colors.danger} />
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
