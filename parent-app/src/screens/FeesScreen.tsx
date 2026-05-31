import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

const mockFees = [
  { id: '1', title: 'Term 1 Fee', amount: 5000, dueDate: '2024-01-31', status: 'paid' },
  { id: '2', title: 'Term 2 Fee', amount: 5000, dueDate: '2024-04-30', status: 'pending' },
  { id: '3', title: 'Transport Fee', amount: 12000, dueDate: '2024-02-28', status: 'overdue' },
];

export function FeesScreen() {
  const [fees, setFees] = useState<any[]>([]);
  useEffect(() => {
    apiRequest('/fees/student/1').then(d => {
      if (d?.pending || d?.paid) {
        setFees([...(d.pending || []), ...(d.paid || [])]);
      }
    }).catch(() => {});
  }, []);

  const feeRecords = fees.length > 0 ? fees : mockFees;
  const total = feeRecords.reduce((s: number, f: any) => s + Number(f.amount), 0);
  const paid = feeRecords.filter((f: any) => f.status === 'paid').reduce((s: number, f: any) => s + Number(f.amount), 0);
  const pending = feeRecords.filter((f: any) => f.status === 'pending' || f.status === 'overdue').reduce((s: number, f: any) => s + Number(f.amount), 0);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Fees</Text>
      </View>
      <ScrollView contentContainerStyle={styles.screenContent}>
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
        {feeRecords.map((fee: any) => (
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

        <TouchableOpacity style={styles.payButton}>
          <Text style={styles.payButtonText}>Pay Now</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
}
