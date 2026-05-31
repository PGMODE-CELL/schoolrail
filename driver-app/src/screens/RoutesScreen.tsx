import React, { useState, useEffect } from 'react';
import { View, Text, ScrollView, SafeAreaView } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

const mockRoutes = [
  { id: '1', name: 'Route 1 - North', students: 32, stops: 8, status: 'active', driver: 'John D.', vehicle: 'SR-001' },
  { id: '2', name: 'Route 2 - East', students: 28, stops: 6, status: 'active', driver: 'Mike R.', vehicle: 'SR-002' },
  { id: '3', name: 'Route 3 - West', students: 25, stops: 5, status: 'active', driver: 'Sarah K.', vehicle: 'SR-003' },
  { id: '4', name: 'Route 4 - South', students: 30, stops: 7, status: 'idle', driver: 'David L.', vehicle: 'SR-004' },
];

export function RoutesScreen() {
  const [routes, setRoutes] = useState<any[]>([]);
  useEffect(() => {
    apiRequest('/routes').then(d => { if (d?.length) setRoutes(d); }).catch(() => {});
  }, []);

  const displayRoutes = routes.length > 0 ? routes : mockRoutes;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>All Routes</Text>
      </View>

      <ScrollView contentContainerStyle={styles.screenContent}>
        {displayRoutes.map((route: any) => (
          <View key={route.id} style={styles.fullRouteCard}>
            <View style={styles.fullRouteHeader}>
              <View>
                <Text style={styles.fullRouteName}>{route.name}</Text>
                <Text style={styles.fullRouteDriver}>Driver: {route.driver_name || route.driver || `ID: ${route.driver_id || ''}`}</Text>
              </View>
              <View style={[styles.routeBadge, { backgroundColor: String(route.status) === 'active' ? '#D1FAE5' : '#F1F5F9' }]}>
                <Text style={[styles.routeBadgeText, { color: String(route.status) === 'active' ? theme.colors.primary : theme.colors.textSecondary }]}>
                  {(typeof route.status === 'string' ? route.status : String(route.status)).charAt(0).toUpperCase() + (typeof route.status === 'string' ? route.status : String(route.status)).slice(1)}
                </Text>
              </View>
            </View>

            <View style={styles.fullRouteDetails}>
              <View style={styles.fullRouteDetail}>
                <Feather name="users" size={16} color={theme.colors.textSecondary} />
                <Text style={styles.fullRouteDetailText}>{route.student_count || (route.stops ? route.stops.length : 0) || route.students || 0} students</Text>
              </View>
              <View style={styles.fullRouteDetail}>
                <Feather name="map-pin" size={16} color={theme.colors.textSecondary} />
                <Text style={styles.fullRouteDetailText}>{route.stop_count || (route.stops ? route.stops.length : 0) || 0} stops</Text>
              </View>
              <View style={styles.fullRouteDetail}>
                <Feather name="truck" size={16} color={theme.colors.textSecondary} />
                <Text style={styles.fullRouteDetailText}>{route.vehicle_name || route.vehicle || `ID: ${route.vehicle_id || ''}`}</Text>
              </View>
            </View>
          </View>
        ))}
      </ScrollView>
    </SafeAreaView>
  );
}
