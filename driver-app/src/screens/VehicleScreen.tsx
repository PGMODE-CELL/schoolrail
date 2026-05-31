import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

export function VehicleScreen() {
  const [vehicle, setVehicle] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchVehicle = () => {
    setLoading(true);
    setError('');
    apiRequest('/vehicles')
      .then(d => { if (d?.length) setVehicle(d[0]); else if (d?.id) setVehicle(d); setLoading(false); })
      .catch(() => { setError('Failed to load vehicle'); setLoading(false); });
  };

  useEffect(() => { fetchVehicle(); }, []);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>My Vehicle</Text>
      </View>

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
              <TouchableOpacity style={styles.vehicleActionBtn}>
                <Feather name="tool" size={20} color={theme.colors.primary} />
                <Text style={styles.vehicleActionText}>Report Issue</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.vehicleActionBtn}>
                <Feather name="calendar" size={20} color={theme.colors.primary} />
                <Text style={styles.vehicleActionText}>Schedule Service</Text>
              </TouchableOpacity>
            </View>
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
