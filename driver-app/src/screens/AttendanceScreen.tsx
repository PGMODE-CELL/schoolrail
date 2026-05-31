import React, { useState } from 'react';
import { View, Text, TouchableOpacity, ScrollView, TextInput, SafeAreaView } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';

const mockAttendance = [
  { studentId: '1', name: 'Amit Sharma', status: 'present', time: '08:15 AM' },
  { studentId: '2', name: 'Priya Patel', status: 'present', time: '08:20 AM' },
  { studentId: '3', name: 'Rahul Verma', status: 'absent', time: '-' },
  { studentId: '4', name: 'Sneha Singh', status: 'present', time: '08:10 AM' },
  { studentId: '5', name: 'Vikram Joshi', status: 'leave', time: '-' },
];

export function AttendanceScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [attendanceData, setAttendanceData] = useState(mockAttendance);

  const markAttendance = (studentId: string, status: string) => {
    setAttendanceData(prev =>
      prev.map(s => s.studentId === studentId ? { ...s, status } : s)
    );
  };

  const presentCount = attendanceData.filter(s => s.status === 'present').length;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Attendance</Text>
        <Text style={styles.screenSubtitle}>Mark attendance for today's trip</Text>
      </View>

      <View style={styles.attendanceSummary}>
        <View style={styles.summaryItem}>
          <Text style={styles.summaryValue}>{presentCount}</Text>
          <Text style={styles.summaryLabel}>Present</Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={[styles.summaryValue, { color: theme.colors.danger }]}>
            {attendanceData.filter(s => s.status === 'absent').length}
          </Text>
          <Text style={styles.summaryLabel}>Absent</Text>
        </View>
        <View style={styles.summaryItem}>
          <Text style={[styles.summaryValue, { color: theme.colors.warning }]}>
            {attendanceData.filter(s => s.status === 'leave').length}
          </Text>
          <Text style={styles.summaryLabel}>Leave</Text>
        </View>
      </View>

      <View style={styles.searchContainer}>
        <Feather name="search" size={20} color={theme.colors.textSecondary} style={styles.searchIcon} />
        <TextInput
          style={styles.searchInput}
          placeholder="Search student..."
          value={searchQuery}
          onChangeText={setSearchQuery}
        />
      </View>

      <ScrollView style={styles.studentList}>
        {attendanceData.map((student) => (
          <View key={student.studentId} style={styles.studentCard}>
            <View style={styles.studentInfo}>
              <Text style={styles.studentName}>{student.name}</Text>
              <Text style={styles.studentTime}>{student.time}</Text>
            </View>
            <View style={styles.attendanceButtons}>
              <TouchableOpacity
                style={[styles.attendanceBtn, student.status === 'present' && styles.attendanceBtnActive]}
                onPress={() => markAttendance(student.studentId, 'present')}
              >
                <Text style={[styles.btnText, student.status === 'present' && styles.btnTextActive]}>P</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.attendanceBtn, student.status === 'absent' && styles.attendanceBtnAbsent]}
                onPress={() => markAttendance(student.studentId, 'absent')}
              >
                <Text style={[styles.btnText, student.status === 'absent' && styles.btnTextActive]}>A</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={[styles.attendanceBtn, student.status === 'leave' && styles.attendanceBtnLeave]}
                onPress={() => markAttendance(student.studentId, 'leave')}
              >
                <Text style={[styles.btnText, student.status === 'leave' && styles.btnTextActive]}>L</Text>
              </TouchableOpacity>
            </View>
          </View>
        ))}
      </ScrollView>

      <TouchableOpacity style={styles.submitButton}>
        <Text style={styles.submitButtonText}>Submit Attendance</Text>
      </TouchableOpacity>
    </SafeAreaView>
  );
}
