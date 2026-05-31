import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator, Alert, TextInput } from 'react-native';
import { Feather } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest, isOnline, syncEngine } from '../config';

export function VehicleScreen() {
  const [vehicle, setVehicle] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showingCached, setShowingCached] = useState(false);
  const [reportingIssue, setReportingIssue] = useState(false);
  const [issueText, setIssueText] = useState('');

  const fetchVehicle = async () => {
    setLoading(true);
    setError('');
    setShowingCached(false);

    const online = await isOnline();
    if (!online) {
      const cached = await AsyncStorage.getItem('driver_vehicle');
      if (cached) {
        setVehicle(JSON.parse(cached));
        setShowingCached(true);
      }
      setLoading(false);
      return;
    }

    try {
      const d = await apiRequest('/vehicles');
      if (d?.length) {
        setVehicle(d[0]);
        await AsyncStorage.setItem('driver_vehicle', JSON.stringify(d[0]));
      } else if (d?.id) {
        setVehicle(d);
        await AsyncStorage.setItem('driver_vehicle', JSON.stringify(d));
      }
    } catch {
      const cached = await AsyncStorage.getItem('driver_vehicle');
      if (cached) {
        setVehicle(JSON.parse(cached));
        setShowingCached(true);
      } else {
        setError('Failed to load vehicle');
      }
    }
    setLoading(false);
  };

  useEffect(() => { fetchVehicle(); }, []);

  const handleReportIssue = async () => {
    if (!issueText.trim()) return;
    await syncEngine.enqueue({
      type: 'CREATE',
      resource: 'maintenance_issue',
      data: { vehicleId: vehicle?.id, description: issueText.trim(), reportedAt: new Date().toISOString() },
    });
    setIssueText('');
    setReportingIssue(false);
    Alert.alert('Issue Reported', 'Maintenance issue will be submitted when online.');
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>My Vehicle</Text>
      </View>

      {showingCached ? (
        <View style={{ backgroundColor: '#FEF3C7', padding: 8, alignItems: 'center' }}>
          <Text style={{ fontSize: 12, color: '#92400E', fontWeight: '500' }}>Showing cached data</Text>
        </View>
      ) : null}

      <ScrollView contentContainerStyle={styles.screenContent}>
        {loading ? (
          <ActivityIndicator size="large" color={theme.colors.primary} style={{ marginVertical: 40 }} />
        ) : error ? (
          <View style={{ alignItems: 'center', paddingVertical: 32 }}>
            <Feather name="alert-circle" size={40} color={theme.colors.danger} />
            <Text style={{ color: theme.colors.textSecondary, marginTop: 12, marginBottom: 16 }}>{error}</Text>
            <TouchableOpacity onPress={fetchVehicle} style={{ backgroundColor: theme.colors.primary, paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8 }}>
              <Text style={{ color: 'white', fontWeight: '600' }}>Retry</Text>
            </TouchableOpacity>
          </View>
        ) : !vehicle ? (
          <View style={{ alignItems: 'center', paddingVertical: 32 }}>
            <Feather name="truck" size={40} color={theme.colors.textSecondary} />
            <Text style={{ color: theme.colors.textSecondary, marginTop: 12 }}>No vehicle assigned</Text>
          </View>
        ) : (
          <>
            <View style={styles.vehicleCard}>
              <View style={styles.vehicleHeader}>
                <Text style={styles.vehicleNumber}>{vehicle.reg_number || vehicle.vehicle_number || vehicle.number || ''}</Text>
                <View style={[styles.vehicleStatus, { backgroundColor: String(vehicle.status) === 'active' ? '#D1FAE5' : '#FEF3C7' }]}>
                  <Text style={[styles.vehicleStatusText, { color: String(vehicle.status) === 'active' ? theme.colors.primary : theme.colors.warning }]}>
                    {(typeof vehicle.status === 'string' ? vehicle.status : String(vehicle.status)).charAt(0).toUpperCase() + (typeof vehicle.status === 'string' ? vehicle.status : String(vehicle.status)).slice(1)}
                  </Text>
                </View>
              </View>

              <Text style={styles.vehicleType}>{vehicle.vehicle_type || vehicle.type || ''} • {vehicle.seating_capacity || vehicle.capacity || 0} seats</Text>

              <View style={styles.fuelContainer}>
                <View style={styles.fuelHeader}>
                  <Text style={styles.fuelLabel}>Fuel Level</Text>
                  <Text style={styles.fuelValue}>{vehicle.fuel || vehicle.fuel_level || 0}%</Text>
                </View>
                <View style={styles.fuelBar}>
                  <View style={[styles.fuelProgress, { width: `${vehicle.fuel || vehicle.fuel_level || 0}%` }]} />
                </View>
              </View>

              <View style={styles.vehicleStats}>
                <View style={styles.vehicleStat}>
                  <Text style={styles.vehicleStatLabel}>Last Service</Text>
                  <Text style={styles.vehicleStatValue}>{vehicle.last_service || 'N/A'}</Text>
                </View>
                <View style={styles.vehicleStat}>
                  <Text style={styles.vehicleStatLabel}>Next Service</Text>
                  <Text style={styles.vehicleStatValue}>{vehicle.next_service || 'N/A'}</Text>
                </View>
              </View>
            </View>

            <View style={styles.vehicleActions}>
              <TouchableOpacity style={styles.vehicleActionBtn} onPress={() => setReportingIssue(true)}>
                <Feather name="tool" size={20} color={theme.colors.primary} />
                <Text style={styles.vehicleActionText}>Report Issue</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.vehicleActionBtn}>
                <Feather name="calendar" size={20} color={theme.colors.primary} />
                <Text style={styles.vehicleActionText}>Schedule Service</Text>
              </TouchableOpacity>
            </View>

            {reportingIssue && (
              <View style={{ marginTop: 16, backgroundColor: 'white', borderRadius: 12, padding: 16 }}>
                <TextInput
                  style={{ backgroundColor: '#F8FAFC', borderRadius: 8, padding: 12, fontSize: 14, minHeight: 80, textAlignVertical: 'top' }}
                  placeholder="Describe the issue..."
                  value={issueText}
                  onChangeText={setIssueText}
                  multiline
                />
                <View style={{ flexDirection: 'row', marginTop: 12, gap: 12 }}>
                  <TouchableOpacity
                    onPress={() => { setReportingIssue(false); setIssueText(''); }}
                    style={{ flex: 1, backgroundColor: '#F1F5F9', borderRadius: 8, padding: 12, alignItems: 'center' }}
                  >
                    <Text style={{ fontSize: 14, color: theme.colors.text }}>Cancel</Text>
                  </TouchableOpacity>
                  <TouchableOpacity
                    onPress={handleReportIssue}
                    style={{ flex: 1, backgroundColor: theme.colors.primary, borderRadius: 8, padding: 12, alignItems: 'center' }}
                  >
                    <Text style={{ fontSize: 14, color: 'white', fontWeight: '600' }}>Submit</Text>
                  </TouchableOpacity>
                </View>
              </View>
            )}
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
