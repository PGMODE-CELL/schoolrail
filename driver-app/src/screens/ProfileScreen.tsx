import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator, Alert, TextInput } from 'react-native';
import { Feather } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../theme';
import { styles } from '../styles';
import { useAuth } from '../context/AuthContext';
import { apiRequest, isOnline, syncEngine } from '../config';

export function ProfileScreen() {
  const { user: authUser, logout, updateUser } = useAuth();
  const [profile, setProfile] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showingCached, setShowingCached] = useState(false);
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editPhone, setEditPhone] = useState('');

  const fetchProfile = async () => {
    setLoading(true);
    setError('');
    setShowingCached(false);

    const online = await isOnline();
    if (!online) {
      const stored = await AsyncStorage.getItem('driver_profile');
      if (stored) {
        setProfile(JSON.parse(stored));
        setShowingCached(true);
      }
      setLoading(false);
      return;
    }

    try {
      const d = await apiRequest('/auth/me');
      setProfile(d);
      await AsyncStorage.setItem('driver_profile', JSON.stringify(d));
    } catch {
      const stored = await AsyncStorage.getItem('driver_profile');
      if (stored) {
        setProfile(JSON.parse(stored));
        setShowingCached(true);
      } else {
        setError('Failed to load profile');
      }
    }
    setLoading(false);
  };

  useEffect(() => { fetchProfile(); }, []);

  const u = profile || authUser;

  const handleEdit = () => {
    setEditName(u?.full_name || '');
    setEditPhone(u?.phone || '');
    setEditing(true);
  };

  const handleSave = async () => {
    await syncEngine.enqueue({
      type: 'UPDATE',
      resource: 'profile',
      data: { full_name: editName, phone: editPhone },
    });
    const updatedUser = { ...u, full_name: editName, phone: editPhone };
    await updateUser(updatedUser);
    setProfile(updatedUser);
    await AsyncStorage.setItem('driver_profile', JSON.stringify(updatedUser));
    setEditing(false);
    Alert.alert('Saved', 'Profile changes will sync when online.');
  };

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
              <Text style={styles.profileName}>{u?.full_name}</Text>
              <Text style={styles.profileRole}>{u?.role ? u.role.charAt(0).toUpperCase() + u.role.slice(1) : ''}</Text>
            </View>

            {editing ? (
              <View style={styles.profileSection}>
                <Text style={styles.profileLabel}>Edit Profile</Text>
                <View style={styles.profileInfoCard}>
                  <View style={styles.profileInfoRow}>
                    <Text style={styles.profileInfoLabel}>Name</Text>
                    <TextInput
                      style={{ flex: 1, textAlign: 'right', fontSize: 14, color: theme.colors.text }}
                      value={editName}
                      onChangeText={setEditName}
                    />
                  </View>
                  <View style={styles.profileInfoRow}>
                    <Text style={styles.profileInfoLabel}>Phone</Text>
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
              <>
                <View style={styles.profileSection}>
                  <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text style={styles.profileLabel}>Personal Info</Text>
                    <TouchableOpacity onPress={handleEdit}>
                      <Feather name="edit-2" size={18} color={theme.colors.primary} />
                    </TouchableOpacity>
                  </View>
                  <View style={styles.profileInfoCard}>
                    <View style={styles.profileInfoRow}>
                      <Text style={styles.profileInfoLabel}>Phone</Text>
                      <Text style={styles.profileInfoValue}>{u?.phone}</Text>
                    </View>
                    <View style={styles.profileInfoRow}>
                      <Text style={styles.profileInfoLabel}>Email</Text>
                      <Text style={styles.profileInfoValue}>{u?.email}</Text>
                    </View>
                    <View style={styles.profileInfoRow}>
                      <Text style={styles.profileInfoLabel}>License</Text>
                      <Text style={styles.profileInfoValue}>{u?.license}</Text>
                    </View>
                  </View>
                </View>

                <View style={styles.profileSection}>
                  <Text style={styles.profileLabel}>Assigned Vehicle</Text>
                  <View style={styles.profileInfoCard}>
                    <Text style={styles.profileInfoValue}>{u?.vehicle}</Text>
                  </View>
                </View>
              </>
            )}

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
