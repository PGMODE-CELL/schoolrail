import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, SafeAreaView } from 'react-native';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

const mockAttendance = [
  { date: '2024-01-20', status: 'present', pickup: '08:15 AM', drop: '03:30 PM' },
  { date: '2024-01-19', status: 'present', pickup: '08:10 AM', drop: '03:25 PM' },
  { date: '2024-01-18', status: 'absent', pickup: '-', drop: '-' },
  { date: '2024-01-17', status: 'present', pickup: '08:20 AM', drop: '03:35 PM' },
];

export function AttendanceScreen() {
  const [attendance, setAttendance] = useState<any[]>([]);
  useEffect(() => {
    apiRequest('/attendance/daily?attendance_date=' + new Date().toISOString().slice(0,10))
      .then(d => { if (d?.length) setAttendance(d); }).catch(() => {});
  }, []);

  const records = attendance.length > 0 ? attendance : mockAttendance;
  const present = records.filter((r: any) => r.status === 'present').length;
  const absent = records.filter((r: any) => r.status === 'absent').length;
  const leave = records.filter((r: any) => r.status === 'leave').length;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Attendance</Text>
      </View>
      <ScrollView contentContainerStyle={styles.screenContent}>
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
        {records.map((record: any, index: number) => (
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
      </ScrollView>
    </SafeAreaView>
  );
}
