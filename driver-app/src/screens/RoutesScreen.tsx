import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

export function RoutesScreen() {
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchRoutes = () => {
    setLoading(true);
    setError('');
    apiRequest('/routes')
      .then(d => { if (d?.length) setRoutes(d); setLoading(false); })
      .catch(() => { setError('Failed to load routes'); setLoading(false); });
  };

  useEffect(() => { fetchRoutes(); }, []);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>All Routes</Text>
      </View>

      <ScrollView contentContainerStyle={styles.screenContent}>
        {loading ? (
          <ActivityIndicator size="large" color={theme.colors.primary} style={{ marginVertical: 40 }} />
        ) : error ? (
          <View style={{ alignItems: 'center', paddingVertical: 32 }}>
            <Feather name="alert-circle" size={40} color={theme.colors.danger} />
            <Text style={{ color: theme.colors.textSecondary, marginTop: 12, marginBottom: 16 }}>{error}</Text>
            <TouchableOpacity onPress={fetchRoutes} style={{ backgroundColor: theme.colors.primary, paddingHorizontal: 20, paddingVertical: 10, borderRadius: 8 }}>
              <Text style={{ color: 'white', fontWeight: '600' }}>Retry</Text>
            </TouchableOpacity>
          </View>
        ) : routes.length === 0 ? (
          <View style={{ alignItems: 'center', paddingVertical: 32 }}>
            <Feather name="map" size={40} color={theme.colors.textSecondary} />
            <Text style={{ color: theme.colors.textSecondary, marginTop: 12 }}>No routes assigned</Text>
          </View>
        ) : (
          routes.map((route: any) => (
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
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
