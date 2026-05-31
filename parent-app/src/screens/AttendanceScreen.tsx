import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, SafeAreaView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { Feather } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest, isOnline, syncEngine } from '../config';

export function AttendanceScreen() {
  const [attendance, setAttendance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showingCached, setShowingCached] = useState(false);
  const [pendingSync, setPendingSync] = useState<any[]>([]);

  const loadCachedAttendance = useCallback(async () => {
    const cached = await AsyncStorage.getItem('parent_attendance');
    if (cached) {
      setAttendance(JSON.parse(cached));
      setShowingCached(true);
    }
  }, []);

  const fetchAttendance = useCallback(async () => {
    setLoading(true);
    setError('');
    setShowingCached(false);

    const online = await isOnline();
    if (!online) {
      await loadCachedAttendance();
      setLoading(false);
      return;
    }

    try {
      const d = await apiRequest('/attendance/daily?attendance_date=' + new Date().toISOString().slice(0,10));
      if (Array.isArray(d)) {
        setAttendance(d);
        await AsyncStorage.setItem('parent_attendance', JSON.stringify(d));
      }
    } catch (e: any) {
      await loadCachedAttendance();
      if (!showingCached) setError(e.message || 'Failed to fetch attendance');
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAttendance(); }, [fetchAttendance]);

  useEffect(() => {
    const checkPending = async () => {
      const queue = await AsyncStorage.getItem('sync_queue');
      if (queue) {
        const parsed = JSON.parse(queue);
        setPendingSync(parsed.filter((op: any) => op.resource === 'attendance'));
      }
    };
    const interval = setInterval(checkPending, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.screenHeader}>
          <Text style={styles.screenTitle}>Attendance</Text>
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
          <Text style={styles.screenTitle}>Attendance</Text>
        </View>
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
          <Feather name="alert-circle" size={48} color={theme.colors.danger} />
          <Text style={{ fontSize: 16, color: theme.colors.textSecondary, marginTop: 16, textAlign: 'center' }}>{error}</Text>
          <TouchableOpacity
            onPress={fetchAttendance}
            style={{ marginTop: 16, backgroundColor: theme.colors.primary, borderRadius: 12, paddingHorizontal: 24, paddingVertical: 12 }}
          >
            <Text style={{ color: 'white', fontSize: 14, fontWeight: '600' }}>Retry</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const present = attendance.filter((r: any) => r.status === 'present').length;
  const absent = attendance.filter((r: any) => r.status === 'absent').length;
  const leave = attendance.filter((r: any) => r.status === 'leave').length;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Attendance</Text>
      </View>

      {showingCached ? (
        <View style={{ backgroundColor: '#FEF3C7', padding: 8, alignItems: 'center' }}>
          <Text style={{ fontSize: 12, color: '#92400E', fontWeight: '500' }}>Showing cached data</Text>
        </View>
      ) : null}

      {pendingSync.length > 0 ? (
        <View style={{ backgroundColor: '#DBEAFE', padding: 8, alignItems: 'center' }}>
          <Text style={{ fontSize: 12, color: '#1E40AF', fontWeight: '500' }}>
            {pendingSync.length} change{pendingSync.length > 1 ? 's' : ''} pending sync
          </Text>
        </View>
      ) : null}

      <ScrollView contentContainerStyle={styles.screenContent}>
        {attendance.length > 0 ? (
          <>
            <View style={styles.attendanceStats}>
              <View style={styles.attendanceStat}>
                <Text style={styles.attendanceValue}>{present}</Text>
                <Text style={styles.attendanceLabel}>Present</Text>
              </View>
              <View style={styles.attendanceStat}>
                <Text style={[styles.attendanceValue, { color: theme.colors.danger }]}>{absent}</Text>
                <Text style={styles.attendanceLabel}>Absent</Text>
              </View>
              <View style={styles.attendanceStat}>
                <Text style={[styles.attendanceValue, { color: theme.colors.warning }]}>{leave}</Text>
                <Text style={styles.attendanceLabel}>Leave</Text>
              </View>
            </View>

            <Text style={styles.sectionTitle}>Attendance History</Text>
            {attendance.map((record: any, index: number) => {
              const isPending = pendingSync.some((op: any) => op.data?.recordId === record.id);
              return (
                <View key={index} style={styles.attendanceCard}>
                  <View style={styles.attendanceDate}>
                    <Text style={styles.dateDay}>{new Date(record.date).getDate()}</Text>
                    <Text style={styles.dateMonth}>{new Date(record.date).toLocaleString('default', { month: 'short' })}</Text>
                  </View>
                  <View style={styles.attendanceDetails}>
                    <View style={styles.attendanceStatus}>
                      <View style={[styles.statusDot, {
                        backgroundColor: record.status === 'present' ? theme.colors.success :
                                   record.status === 'absent' ? theme.colors.danger : theme.colors.warning
                      }]} />
                      <Text style={styles.statusText}>{record.status.charAt(0).toUpperCase() + record.status.slice(1)}</Text>
                      {isPending && (
                        <Feather name="clock" size={12} color={theme.colors.warning} style={{ marginLeft: 8 }} />
                      )}
                    </View>
                    <Text style={styles.timeText}>Pickup: {record.pickup}</Text>
                    <Text style={styles.timeText}>Drop: {record.drop}</Text>
                  </View>
                </View>
              );
            })}
          </>
        ) : (
          <View style={{ alignItems: 'center', paddingVertical: 40 }}>
            <Feather name="calendar" size={48} color={theme.colors.textSecondary} />
            <Text style={{ fontSize: 16, color: theme.colors.textSecondary, marginTop: 16 }}>No attendance data yet</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
