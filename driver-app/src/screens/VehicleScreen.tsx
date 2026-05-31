import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

const mockVehicles = [
  { id: '1', number: 'SR-001', type: 'Bus', capacity: 50, status: 'active', fuel: 85 },
  { id: '2', number: 'SR-002', type: 'Van', capacity: 15, status: 'active', fuel: 60 },
  { id: '3', number: 'SR-003', type: 'Bus', capacity: 50, status: 'maintenance', fuel: 45 },
  { id: '4', number: 'SR-004', type: 'Van', capacity: 15, status: 'active', fuel: 90 },
];

export function VehicleScreen() {
  const [vehicles, setVehicles] = useState<any[]>([]);
  useEffect(() => {
    apiRequest('/vehicles').then(d => { if (d?.length) setVehicles(d); }).catch(() => {});
  }, []);

  const displayVehicles = vehicles.length > 0 ? vehicles : mockVehicles;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>My Vehicle</Text>
      </View>

      <ScrollView contentContainerStyle={styles.screenContent}>
        {displayVehicles.slice(0, 1).map((vehicle: any) => (
          <View key={vehicle.id} style={styles.vehicleCard}>
            <View style={styles.vehicleHeader}>
              <Text style={styles.vehicleNumber}>{vehicle.reg_number || vehicle.vehicle_number || vehicle.number}</Text>
              <View style={[styles.vehicleStatus, { backgroundColor: String(vehicle.status) === 'active' ? '#D1FAE5' : '#FEF3C7' }]}>
                <Text style={[styles.vehicleStatusText, { color: String(vehicle.status) === 'active' ? theme.colors.primary : theme.colors.warning }]}>
                  {(typeof vehicle.status === 'string' ? vehicle.status : String(vehicle.status)).charAt(0).toUpperCase() + (typeof vehicle.status === 'string' ? vehicle.status : String(vehicle.status)).slice(1)}
                </Text>
              </View>
            </View>

            <Text style={styles.vehicleType}>{vehicle.vehicle_type || vehicle.type} • {vehicle.seating_capacity || vehicle.capacity} seats</Text>

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
                <Text style={styles.vehicleStatValue}>Jan 15, 2024</Text>
              </View>
              <View style={styles.vehicleStat}>
                <Text style={styles.vehicleStatLabel}>Next Service</Text>
                <Text style={styles.vehicleStatValue}>Feb 15, 2024</Text>
              </View>
            </View>
          </View>
        ))}

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
      </ScrollView>
    </SafeAreaView>
  );
}
