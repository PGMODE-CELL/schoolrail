import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';
import { useAuth } from '../context/AuthContext';

const mockChildren = [
  { id: '1', name: 'Aryan Sharma', class: 'Class 5-A', route: 'Route 1', vehicle: 'SR-001' },
  { id: '2', name: 'Priya Sharma', class: 'Class 3-B', route: 'Route 2', vehicle: 'SR-003' },
];

export function ProfileScreen() {
  const { user: authUser, logout } = useAuth();
  const [students, setStudents] = useState<any[]>([]);

  useEffect(() => {
    apiRequest('/students/').then(d => { if (d?.length) setStudents(d); }).catch(() => {});
  }, []);

  const displayChildren = students.length > 0
    ? students.map((s: any) => ({ id: String(s.id), name: s.full_name || `${s.first_name} ${s.last_name}`, class: s.class_name || '', route: s.route_name || '', vehicle: s.vehicle_name || '' }))
    : mockChildren;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Profile</Text>
      </View>
      <ScrollView contentContainerStyle={styles.screenContent}>
        <View style={styles.profileHeader}>
          <View style={styles.profileAvatar}>
            <Text style={styles.profileInitial}>{(authUser?.full_name || 'P')[0]}</Text>
          </View>
          <Text style={styles.profileName}>{authUser?.full_name || 'Parent User'}</Text>
          <Text style={styles.profileEmail}>{authUser?.email || 'parent@example.com'}</Text>
        </View>

        <View style={styles.profileSection}>
          <Text style={styles.sectionTitle}>Personal Information</Text>
          <View style={styles.profileInfo}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Phone</Text>
              <Text style={styles.infoValue}>{authUser?.phone || '+91 9876543210'}</Text>
            </View>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>Email</Text>
              <Text style={styles.infoValue}>{authUser?.email || 'parent@example.com'}</Text>
            </View>
          </View>
        </View>

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
                <Text style={styles.childInfoRoute}>{child.route} • {child.vehicle}</Text>
              </View>
            </View>
          ))}
        </View>

        <TouchableOpacity style={styles.logoutButton} onPress={logout}>
          <Feather name="log-out" size={20} color={theme.colors.danger} />
          <Text style={styles.logoutText}>Logout</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
