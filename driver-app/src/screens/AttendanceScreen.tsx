import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, TextInput, SafeAreaView, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

export function AttendanceScreen() {
  const [searchQuery, setSearchQuery] = useState('');
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const fetchStudents = () => {
    setLoading(true);
    setError('');
    apiRequest('/attendance/students')
      .then(d => { if (d?.length) setStudents(d); setLoading(false); })
      .catch(() => { setError('Failed to load students'); setLoading(false); });
  };

  useEffect(() => { fetchStudents(); }, []);

  const markAttendance = (studentId: string, status: string) => {
    setStudents(prev =>
      prev.map(s => (s.student_id || s.id || s.studentId) === studentId ? { ...s, status } : s)
    );
  };

  const submitAttendance = async () => {
    setSubmitting(true);
    setSubmitError('');
    try {
      await apiRequest('/attendance', {
        method: 'POST',
        body: JSON.stringify({ attendance: students }),
      });
    } catch {
      setSubmitError('Failed to submit attendance');
    }
    setSubmitting(false);
  };

  const filtered = students.filter((s: any) =>
    (s.name || '').toLowerCase().includes(searchQuery.toLowerCase())
  );

  const presentCount = students.filter((s: any) => s.status === 'present').length;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Attendance</Text>
        <Text style={styles.screenSubtitle}>Mark attendance for today's trip</Text>
      </View>

      {loading ? (
        <ActivityIndicator size="large" color={theme.colors.primary} style={{ marginVertical: 40 }} />
      ) : error ? (
        <View style={{ alignItems: 'center', paddingVertical: 32 }}>
          <Feather name="alert-circle" size={40} color={theme.colors.danger} />
          <Text style={{ color: theme.colors.textSecondary, marginTop: 12, marginBottom: 16 }}>{error}</Text>
          <TouchableOpacity onPress={fetchStudents} style={{ backgroundColor: theme.colors.primary, paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8 }}>
            <Text style={{ color: 'white', fontWeight: '600' }}>Retry</Text>
          </TouchableOpacity>
        </View>
      ) : students.length === 0 ? (
        <View style={{ alignItems: 'center', paddingVertical: 32 }}>
          <Feather name="users" size={40} color={theme.colors.textSecondary} />
          <Text style={{ color: theme.colors.textSecondary, marginTop: 12 }}>No students assigned for today</Text>
        </View>
      ) : (
        <>
          <View style={styles.attendanceSummary}>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryValue}>{presentCount}</Text>
              <Text style={styles.summaryLabel}>Present</Text>
            </View>
            <View style={styles.summaryItem}>
              <Text style={[styles.summaryValue, { color: theme.colors.danger }]}>
                {students.filter((s: any) => s.status === 'absent').length}
              </Text>
              <Text style={styles.summaryLabel}>Absent</Text>
            </View>
            <View style={styles.summaryItem}>
              <Text style={[styles.summaryValue, { color: theme.colors.warning }]}>
                {students.filter((s: any) => s.status === 'leave').length}
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
            {filtered.length === 0 ? (
              <View style={{ alignItems: 'center', paddingVertical: 20 }}>
                <Text style={{ color: theme.colors.textSecondary }}>No matching students</Text>
              </View>
            ) : (
              filtered.map((student: any) => {
                const sid = student.student_id || student.id || student.studentId;
                return (
                  <View key={sid} style={styles.studentCard}>
                    <View style={styles.studentInfo}>
                      <Text style={styles.studentName}>{student.name}</Text>
                      <Text style={styles.studentTime}>{student.time || '-'}</Text>
                    </View>
                    <View style={styles.attendanceButtons}>
                      <TouchableOpacity
                        style={[styles.attendanceBtn, student.status === 'present' && styles.attendanceBtnActive]}
                        onPress={() => markAttendance(sid, 'present')}
                      >
                        <Text style={[styles.btnText, student.status === 'present' && styles.btnTextActive]}>P</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={[styles.attendanceBtn, student.status === 'absent' && styles.attendanceBtnAbsent]}
                        onPress={() => markAttendance(sid, 'absent')}
                      >
                        <Text style={[styles.btnText, student.status === 'absent' && styles.btnTextActive]}>A</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={[styles.attendanceBtn, student.status === 'leave' && styles.attendanceBtnLeave]}
                        onPress={() => markAttendance(sid, 'leave')}
                      >
                        <Text style={[styles.btnText, student.status === 'leave' && styles.btnTextActive]}>L</Text>
                      </TouchableOpacity>
                    </View>
                  </View>
                );
              })
            )}
          </ScrollView>

          {submitError ? (
            <Text style={{ color: theme.colors.danger, fontSize: 12, textAlign: 'center', marginBottom: 4 }}>{submitError}</Text>
          ) : null}

          <TouchableOpacity style={styles.submitButton} onPress={submitAttendance} disabled={submitting}>
            {submitting ? (
              <ActivityIndicator color="white" />
            ) : (
              <Text style={styles.submitButtonText}>Submit Attendance</Text>
            )}
          </TouchableOpacity>
        </>
      )}
    </SafeAreaView>
  );
}
