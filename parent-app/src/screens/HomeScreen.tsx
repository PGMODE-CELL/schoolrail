import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { LinearGradient } from 'expo-linear-gradient';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';
import { useAuth } from '../context/AuthContext';

export function HomeScreen() {
  const navigation = useNavigation<any>();
  const { user } = useAuth();
  const [selectedChild, setSelectedChild] = useState<any>(null);
  const [students, setStudents] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [attendance, setAttendance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const [s, n] = await Promise.all([
        apiRequest('/students/'),
        apiRequest('/notifications/'),
      ]);
      if (Array.isArray(s)) {
        setStudents(s);
        if (s.length > 0) setSelectedChild(s[0]);
      }
      if (Array.isArray(n)) setNotifications(n);
      try {
        const d = await apiRequest('/attendance/daily?attendance_date=' + new Date().toISOString().slice(0,10));
        if (Array.isArray(d)) setAttendance(d);
      } catch {}
    } catch (e: any) {
      setError(e.message || 'Failed to load dashboard data');
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchData(); }, [fetchData]);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <LinearGradient colors={[theme.colors.primary, theme.colors.secondary]} style={styles.header}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.greeting}>Welcome back!</Text>
              <Text style={styles.userName}>{user?.full_name || ''}</Text>
            </View>
          </View>
        </LinearGradient>
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      </SafeAreaView>
    );
  }

  if (error) {
    return (
      <SafeAreaView style={styles.container}>
        <LinearGradient colors={[theme.colors.primary, theme.colors.secondary]} style={styles.header}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.greeting}>Welcome back!</Text>
              <Text style={styles.userName}>{user?.full_name || ''}</Text>
            </View>
          </View>
        </LinearGradient>
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
          <Feather name="alert-circle" size={48} color={theme.colors.danger} />
          <Text style={{ fontSize: 16, color: theme.colors.textSecondary, marginTop: 16, textAlign: 'center' }}>{error}</Text>
          <TouchableOpacity
            onPress={fetchData}
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
    route: '',
    vehicle: '',
  }));

  const displayNotifications = notifications.map((n: any) => ({
    id: String(n.id),
    title: n.title,
    message: n.message,
    time: n.created_at || '',
    read: n.is_read,
  }));

  const totalAtt = attendance.length;
  const presentCount = attendance.filter((a: any) => a.status === 'present').length;

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <LinearGradient colors={[theme.colors.primary, theme.colors.secondary]} style={styles.header}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.greeting}>Welcome back!</Text>
              <Text style={styles.userName}>{user?.full_name || ''}</Text>
            </View>
            <TouchableOpacity style={styles.notificationBtn}>
              <Feather name="bell" size={24} color="white" />
              <View style={styles.badge} />
            </TouchableOpacity>
          </View>

          {displayChildren.length > 0 && (
            <View style={styles.childSelector}>
              <Text style={styles.selectorLabel}>Select Child</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                {displayChildren.map((child: any) => (
                  <TouchableOpacity
                    key={child.id}
                    style={[styles.childCard, selectedChild?.id === child.id && styles.childCardSelected]}
                    onPress={() => setSelectedChild(child)}
                  >
                    <View style={styles.childAvatar}>
                      <Text style={styles.childInitial}>{child.name[0]}</Text>
                    </View>
                    <Text style={[styles.childName, selectedChild?.id === child.id && styles.childNameSelected]}>
                      {child.name.split(' ')[0]}
                    </Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
            </View>
          )}
        </LinearGradient>

        <View style={styles.content}>
          {attendance.length > 0 ? (
            <View style={styles.statsRow}>
              <View style={styles.statCard}>
                <Text style={styles.statValue}>{Math.round(presentCount / totalAtt * 100)}%</Text>
                <Text style={styles.statLabel}>Attendance</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statValue}>{presentCount}</Text>
                <Text style={styles.statLabel}>Days Present</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statValue}>{totalAtt}</Text>
                <Text style={styles.statLabel}>Total Days</Text>
              </View>
            </View>
          ) : (
            <View style={styles.statsRow}>
              <View style={styles.statCard}>
                <Text style={styles.statValue}>--</Text>
                <Text style={styles.statLabel}>Attendance</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statValue}>--</Text>
                <Text style={styles.statLabel}>Days Present</Text>
              </View>
              <View style={styles.statCard}>
                <Text style={styles.statValue}>--</Text>
                <Text style={styles.statLabel}>Total Days</Text>
              </View>
            </View>
          )}

          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Recent Activity</Text>
            </View>
            {displayNotifications.length > 0 ? (
              displayNotifications.slice(0, 3).map((item: any) => (
                <View key={item.id} style={styles.activityItem}>
                  <View style={[styles.activityIcon, !item.read && styles.activityIconUnread]}>
                    <Feather name="bell" size={16} color={item.read ? theme.colors.primary : 'white'} />
                  </View>
                  <View style={styles.activityContent}>
                    <Text style={styles.activityTitle}>{item.title}</Text>
                    <Text style={styles.activityMessage}>{item.message}</Text>
                    <Text style={styles.activityTime}>{item.time}</Text>
                  </View>
                </View>
              ))
            ) : (
              <Text style={{ fontSize: 14, color: theme.colors.textSecondary, textAlign: 'center', paddingVertical: 20 }}>
                No notifications yet
              </Text>
            )}
          </View>

          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Quick Actions</Text>
            </View>
            <View style={styles.quickActions}>
              <TouchableOpacity style={styles.quickAction} onPress={() => navigation.navigate('Attendance')}>
                <View style={[styles.quickActionIcon, { backgroundColor: '#EEF2FF' }]}>
                  <Feather name="clock" size={20} color={theme.colors.primary} />
                </View>
                <Text style={styles.quickActionLabel}>Attendance</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.quickAction} onPress={() => navigation.navigate('Fees')}>
                <View style={[styles.quickActionIcon, { backgroundColor: '#ECFDF5' }]}>
                  <Feather name="dollar-sign" size={20} color={theme.colors.success} />
                </View>
                <Text style={styles.quickActionLabel}>Fees</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.quickAction} onPress={() => navigation.navigate('Track')}>
                <View style={[styles.quickActionIcon, { backgroundColor: '#FEF3C7' }]}>
                  <Feather name="map" size={20} color={theme.colors.warning} />
                </View>
                <Text style={styles.quickActionLabel}>Track</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.quickAction} onPress={() => navigation.navigate('Profile')}>
                <View style={[styles.quickActionIcon, { backgroundColor: '#FCE7F3' }]}>
                  <Feather name="user" size={20} color="#EC4899" />
                </View>
                <Text style={styles.quickActionLabel}>Profile</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
