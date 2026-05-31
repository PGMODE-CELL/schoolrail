import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, ScrollView, SafeAreaView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

export function AttendanceScreen() {
  const [attendance, setAttendance] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchAttendance = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const d = await apiRequest('/attendance/daily?attendance_date=' + new Date().toISOString().slice(0,10));
      if (Array.isArray(d)) {
        setAttendance(d);
      }
    } catch (e: any) {
      setError(e.message || 'Failed to fetch attendance');
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchAttendance(); }, [fetchAttendance]);

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

  if (error) {
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
            {attendance.map((record: any, index: number) => (
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
                  </View>
                  <Text style={styles.timeText}>Pickup: {record.pickup}</Text>
                  <Text style={styles.timeText}>Drop: {record.drop}</Text>
                </View>
              </View>
            ))}
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
