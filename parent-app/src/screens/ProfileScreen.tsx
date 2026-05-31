import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator, Alert, TextInput } from 'react-native';
import { Feather } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest, isOnline, syncEngine } from '../config';
import { useAuth } from '../context/AuthContext';

export function ProfileScreen() {
  const { user, logout, updateUser } = useAuth();
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showingCached, setShowingCached] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editPhone, setEditPhone] = useState('');

  const loadCached = useCallback(async () => {
    const cachedStudents = await AsyncStorage.getItem('profile_students');
    if (cachedStudents) {
      setStudents(JSON.parse(cachedStudents));
      setShowingCached(true);
    }
  }, []);

  const fetchStudents = useCallback(async () => {
    setLoading(true);
    setError('');
    setShowingCached(false);

    const online = await isOnline();
    if (!online) {
      await loadCached();
      setLoading(false);
      return;
    }

    try {
      const d = await apiRequest('/students/');
      if (Array.isArray(d)) {
        setStudents(d);
        await AsyncStorage.setItem('profile_students', JSON.stringify(d));
      }
    } catch (e: any) {
      await loadCached();
      if (!showingCached) setError(e.message || 'Failed to fetch students');
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchStudents(); }, [fetchStudents]);

  const handleEdit = () => {
    setEditName(user?.full_name || '');
    setEditPhone(user?.phone || '');
    setEditing(true);
  };

  const handleSave = async () => {
    await syncEngine.enqueue({
      type: 'UPDATE',
      resource: 'profile',
      data: { full_name: editName, phone: editPhone },
    });
    const updatedUser = { ...user, full_name: editName, phone: editPhone };
    await updateUser(updatedUser);
    setEditing(false);
    Alert.alert('Saved', 'Profile changes will sync when online.');
  };

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

  if (error && !showingCached) {
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

      {showingCached ? (
        <View style={{ backgroundColor: '#FEF3C7', padding: 8, alignItems: 'center' }}>
          <Text style={{ fontSize: 12, color: '#92400E', fontWeight: '500' }}>Showing cached data</Text>
        </View>
      ) : null}

      <ScrollView contentContainerStyle={styles.screenContent}>
        <View style={styles.profileHeader}>
          <View style={styles.profileAvatar}>
            <Text style={styles.profileInitial}>{(user?.full_name || 'U')[0]}</Text>
          </View>
          <Text style={styles.profileName}>{user?.full_name}</Text>
          <Text style={styles.profileEmail}>{user?.email}</Text>
        </View>

        {editing ? (
          <View style={styles.profileSection}>
            <Text style={styles.sectionTitle}>Edit Profile</Text>
            <View style={styles.profileInfo}>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Name</Text>
                <TextInput
                  style={{ flex: 1, textAlign: 'right', fontSize: 14, color: theme.colors.text }}
                  value={editName}
                  onChangeText={setEditName}
                />
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Phone</Text>
                <TextInput
                  style={{ flex: 1, textAlign: 'right', fontSize: 14, color: theme.colors.text }}
                  value={editPhone}
                  onChangeText={setEditPhone}
                  keyboardType="phone-pad"
                />
              </View>
            </View>
            <View style={{ flexDirection: 'row', marginTop: 12, gap: 12 }}>
              <TouchableOpacity
                onPress={() => setEditing(false)}
                style={{ flex: 1, backgroundColor: '#F1F5F9', borderRadius: 12, padding: 12, alignItems: 'center' }}
              >
                <Text style={{ fontSize: 14, color: theme.colors.text }}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                onPress={handleSave}
                style={{ flex: 1, backgroundColor: theme.colors.primary, borderRadius: 12, padding: 12, alignItems: 'center' }}
              >
                <Text style={{ fontSize: 14, color: 'white', fontWeight: '600' }}>Save</Text>
              </TouchableOpacity>
            </View>
          </View>
        ) : (
          <View style={styles.profileSection}>
            <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
              <Text style={styles.sectionTitle}>Personal Information</Text>
              <TouchableOpacity onPress={handleEdit}>
                <Feather name="edit-2" size={18} color={theme.colors.primary} />
              </TouchableOpacity>
            </View>
            <View style={styles.profileInfo}>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Phone</Text>
                <Text style={styles.infoValue}>{user?.phone}</Text>
              </View>
              <View style={styles.infoRow}>
                <Text style={styles.infoLabel}>Email</Text>
                <Text style={styles.infoValue}>{user?.email}</Text>
              </View>
            </View>
          </View>
        )}

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
