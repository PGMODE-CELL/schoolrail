import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator, Alert } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

export function FeesScreen() {
  const [fees, setFees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchFees = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const d = await apiRequest('/fees?student_id=1');
      if (d?.pending || d?.paid) {
        setFees([...(d.pending || []), ...(d.paid || [])]);
      }
    } catch (e: any) {
      setError(e.message || 'Failed to fetch fees');
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchFees(); }, [fetchFees]);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.screenHeader}>
          <Text style={styles.screenTitle}>Fees</Text>
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
          <Text style={styles.screenTitle}>Fees</Text>
        </View>
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
          <Feather name="alert-circle" size={48} color={theme.colors.danger} />
          <Text style={{ fontSize: 16, color: theme.colors.textSecondary, marginTop: 16, textAlign: 'center' }}>{error}</Text>
          <TouchableOpacity
            onPress={fetchFees}
            style={{ marginTop: 16, backgroundColor: theme.colors.primary, borderRadius: 12, paddingHorizontal: 24, paddingVertical: 12 }}
          >
            <Text style={{ color: 'white', fontSize: 14, fontWeight: '600' }}>Retry</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const total = fees.reduce((s: number, f: any) => s + Number(f.amount), 0);
  const paid = fees.filter((f: any) => f.status === 'paid').reduce((s: number, f: any) => s + Number(f.amount), 0);
  const pending = fees.filter((f: any) => f.status === 'pending' || f.status === 'overdue').reduce((s: number, f: any) => s + Number(f.amount), 0);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Fees</Text>
      </View>
      <ScrollView contentContainerStyle={styles.screenContent}>
        {fees.length > 0 ? (
          <>
            <View style={styles.feeSummary}>
              <View style={styles.feeSummaryItem}>
                <Text style={styles.feeSummaryLabel}>Total Fees</Text>
                <Text style={styles.feeSummaryValue}>₹{total}</Text>
              </View>
              <View style={styles.feeSummaryItem}>
                <Text style={styles.feeSummaryLabel}>Paid</Text>
                <Text style={[styles.feeSummaryValue, { color: theme.colors.success }]}>₹{paid}</Text>
              </View>
              <View style={styles.feeSummaryItem}>
                <Text style={styles.feeSummaryLabel}>Pending</Text>
                <Text style={[styles.feeSummaryValue, { color: theme.colors.warning }]}>₹{pending}</Text>
              </View>
            </View>

            <Text style={styles.sectionTitle}>Fee History</Text>
            {fees.map((fee: any) => (
              <View key={fee.id} style={styles.feeCard}>
                <View style={styles.feeInfo}>
                  <Text style={styles.feeTitle}>{fee.title}</Text>
                  <Text style={styles.feeDue}>Due: {fee.dueDate}</Text>
                </View>
                <View style={styles.feeAmount}>
                  <Text style={styles.feeValue}>₹{fee.amount}</Text>
                  <View style={[styles.feeStatus, {
                    backgroundColor: fee.status === 'paid' ? '#ECFDF5' :
                               fee.status === 'pending' ? '#FEF3C7' : '#FEE2E2'
                  }]}>
                    <Text style={[styles.feeStatusText, {
                      color: fee.status === 'paid' ? theme.colors.success :
                             fee.status === 'pending' ? theme.colors.warning : theme.colors.danger
                    }]}>
                      {fee.status.charAt(0).toUpperCase() + fee.status.slice(1)}
                    </Text>
                  </View>
                </View>
              </View>
            ))}

            <TouchableOpacity
              style={styles.payButton}
              onPress={() => Alert.alert('Pay Now', 'Payment gateway will be integrated soon.')}
            >
              <Text style={styles.payButtonText}>Pay Now</Text>
            </TouchableOpacity>
          </>
        ) : (
          <View style={{ alignItems: 'center', paddingVertical: 40 }}>
            <Feather name="dollar-sign" size={48} color={theme.colors.textSecondary} />
            <Text style={{ fontSize: 16, color: theme.colors.textSecondary, marginTop: 16 }}>No fee records yet</Text>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
