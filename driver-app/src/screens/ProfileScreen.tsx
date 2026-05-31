import React from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { useAuth } from '../context/AuthContext';

export function ProfileScreen() {
  const { user: authUser, logout } = useAuth();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Profile</Text>
      </View>

      <ScrollView contentContainerStyle={styles.screenContent}>
        <View style={styles.profileHeader}>
          <View style={styles.profileAvatar}>
            <Text style={styles.profileInitial}>{(authUser?.full_name || 'JD').split(' ').map((s: string) => s[0]).join('')}</Text>
          </View>
          <Text style={styles.profileName}>{authUser?.full_name || 'John Driver'}</Text>
          <Text style={styles.profileRole}>Bus Driver</Text>
        </View>

        <View style={styles.profileSection}>
          <Text style={styles.profileLabel}>Personal Info</Text>
          <View style={styles.profileInfoCard}>
            <View style={styles.profileInfoRow}>
              <Text style={styles.profileInfoLabel}>Phone</Text>
              <Text style={styles.profileInfoValue}>{authUser?.phone || '+91 9876543210'}</Text>
            </View>
            <View style={styles.profileInfoRow}>
              <Text style={styles.profileInfoLabel}>Email</Text>
              <Text style={styles.profileInfoValue}>{authUser?.email || 'john@schoolrail.com'}</Text>
            </View>
            <View style={styles.profileInfoRow}>
              <Text style={styles.profileInfoLabel}>License</Text>
              <Text style={styles.profileInfoValue}>{authUser?.license || 'DL-12345678'}</Text>
            </View>
          </View>
        </View>

        <View style={styles.profileSection}>
          <Text style={styles.profileLabel}>Assigned Vehicle</Text>
          <View style={styles.profileInfoCard}>
            <Text style={styles.profileInfoValue}>{authUser?.vehicle || 'SR-001 • Bus (50 seats)'}</Text>
          </View>
        </View>

        <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
          <Feather name="log-out" size={20} color={theme.colors.danger} />
          <Text style={styles.logoutBtnText}>Logout</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
