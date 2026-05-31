import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { LinearGradient } from 'expo-linear-gradient';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

const mockNotifications = [
  { id: '1', title: 'Attendance Marked', message: 'Your child was marked present on Route 1', time: '10 min ago', read: false },
  { id: '2', title: 'Bus Arrived', message: 'Bus SR-001 has arrived at Stop 5', time: '30 min ago', read: false },
  { id: '3', title: 'Fee Payment', message: 'Term 2 fee of ₹5,000 is due', time: '2 hours ago', read: true },
  { id: '4', title: 'Trip Started', message: 'Morning trip has started', time: '3 hours ago', read: true },
];

const mockChildren = [
  { id: '1', name: 'Aryan Sharma', class: 'Class 5-A', route: 'Route 1', vehicle: 'SR-001' },
  { id: '2', name: 'Priya Sharma', class: 'Class 3-B', route: 'Route 2', vehicle: 'SR-003' },
];

const mockAttendance = [
  { date: '2024-01-20', status: 'present', pickup: '08:15 AM', drop: '03:30 PM' },
  { date: '2024-01-19', status: 'present', pickup: '08:10 AM', drop: '03:25 PM' },
  { date: '2024-01-18', status: 'absent', pickup: '-', drop: '-' },
  { date: '2024-01-17', status: 'present', pickup: '08:20 AM', drop: '03:35 PM' },
];

export function HomeScreen() {
  const navigation = useNavigation();
  const [selectedChild, setSelectedChild] = useState(mockChildren[0]);
  const [students, setStudents] = useState<any[]>([]);
  const [notifications, setNotifications] = useState<any[]>([]);
  const [attendance, setAttendance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const [s, n] = await Promise.all([
          apiRequest('/students/').catch(() => []),
          apiRequest('/notifications/').catch(() => []),
        ]);
        if (s?.length) setStudents(s);
        if (n?.length) setNotifications(n);
        apiRequest('/attendance/daily?attendance_date=' + new Date().toISOString().slice(0,10))
          .then(d => { if (d?.length) setAttendance(d); }).catch(() => {});
      } catch {}
      setLoading(false);
    })();
  }, []);

  const displayChildren = students.length > 0
    ? students.map((s: any) => ({ id: String(s.id), name: s.full_name || `${s.first_name} ${s.last_name}`, class: s.class_name || '', route: '', vehicle: '' }))
    : mockChildren;

  const displayNotifications = notifications.length > 0
    ? notifications.map((n: any) => ({ id: String(n.id), title: n.title, message: n.message, time: n.created_at || '', read: n.is_read }))
    : mockNotifications;

  const presentCount = attendance.filter((a: any) => a.status === 'present').length;
  const totalAtt = attendance.length || 12;

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <LinearGradient colors={[theme.colors.primary, theme.colors.secondary]} style={styles.header}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.greeting}>Welcome back!</Text>
              <Text style={styles.userName}>Parent User</Text>
            </View>
            <TouchableOpacity style={styles.notificationBtn}>
              <Feather name="bell" size={24} color="white" />
              <View style={styles.badge} />
            </TouchableOpacity>
          </View>

          <View style={styles.childSelector}>
            <Text style={styles.selectorLabel}>Select Child</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false}>
              {displayChildren.map((child: any) => (
                <TouchableOpacity
                  key={child.id}
                  style={[styles.childCard, selectedChild.id === child.id && styles.childCardSelected]}
                  onPress={() => setSelectedChild(child)}
                >
                  <View style={styles.childAvatar}>
                    <Text style={styles.childInitial}>{child.name[0]}</Text>
                  </View>
                  <Text style={[styles.childName, selectedChild.id === child.id && styles.childNameSelected]}>
                    {child.name.split(' ')[0]}
                  </Text>
                </TouchableOpacity>
              ))}
            </ScrollView>
          </View>
        </LinearGradient>

        <View style={styles.content}>
          <View style={styles.statsRow}>
            <View style={styles.statCard}>
              <Text style={styles.statValue}>{totalAtt > 0 ? Math.round(presentCount / totalAtt * 100) : 98}%</Text>
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

          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Recent Activity</Text>
              <TouchableOpacity>
                <Text style={styles.seeAll}>See All</Text>
              </TouchableOpacity>
            </View>
            {displayNotifications.slice(0, 3).map((item: any) => (
              <View key={item.id} style={styles.activityItem}>
                <View style={[styles.activityIcon, !item.read && styles.activityIconUnread]}>
                  <Feather name="bell" size={16} color={theme.colors.primary} />
                </View>
                <View style={styles.activityContent}>
                  <Text style={styles.activityTitle}>{item.title}</Text>
                  <Text style={styles.activityMessage}>{item.message}</Text>
                  <Text style={styles.activityTime}>{item.time}</Text>
                </View>
              </View>
            ))}
          </View>

          <View style={styles.section}>
            <View style={styles.sectionHeader}>
              <Text style={styles.sectionTitle}>Quick Actions</Text>
            </View>
            <View style={styles.quickActions}>
              <TouchableOpacity style={styles.quickAction}>
                <View style={[styles.quickActionIcon, { backgroundColor: '#EEF2FF' }]}>
                  <Feather name="clock" size={20} color={theme.colors.primary} />
                </View>
                <Text style={styles.quickActionLabel}>Attendance</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.quickAction}>
                <View style={[styles.quickActionIcon, { backgroundColor: '#ECFDF5' }]}>
                  <Feather name="dollar-sign" size={20} color={theme.colors.success} />
                </View>
                <Text style={styles.quickActionLabel}>Fees</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.quickAction}>
                <View style={[styles.quickActionIcon, { backgroundColor: '#FEF3C7' }]}>
                  <Feather name="map" size={20} color={theme.colors.warning} />
                </View>
                <Text style={styles.quickActionLabel}>Track</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.quickAction}>
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
