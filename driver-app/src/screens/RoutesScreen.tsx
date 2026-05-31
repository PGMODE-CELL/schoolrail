import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator } from 'react-native';
import { Feather } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest, isOnline, syncEngine } from '../config';

export function RoutesScreen() {
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showingCached, setShowingCached] = useState(false);
  const [pendingSyncCount, setPendingSyncCount] = useState(0);

  const fetchRoutes = async () => {
    setLoading(true);
    setError('');
    setShowingCached(false);

    const online = await isOnline();
    if (!online) {
      const cached = await AsyncStorage.getItem('driver_routes');
      if (cached) {
        setRoutes(JSON.parse(cached));
        setShowingCached(true);
      }
      setLoading(false);
      return;
    }

    try {
      const d = await apiRequest('/routes');
      if (d?.length) {
        setRoutes(d);
        await AsyncStorage.setItem('driver_routes', JSON.stringify(d));
      }
    } catch {
      const cached = await AsyncStorage.getItem('driver_routes');
      if (cached) {
        setRoutes(JSON.parse(cached));
        setShowingCached(true);
      } else {
        setError('Failed to load routes');
      }
    }
    setLoading(false);
  };

  useEffect(() => { fetchRoutes(); }, []);

  useEffect(() => {
    const checkPending = async () => {
      const queue = await AsyncStorage.getItem('sync_queue');
      if (queue) {
        const parsed = JSON.parse(queue);
        setPendingSyncCount(parsed.filter((op: any) => op.resource === 'stop_arrival').length);
      }
    };
    const interval = setInterval(checkPending, 5000);
    return () => clearInterval(interval);
  }, []);

  const markArrival = async (routeId: string, stopId: string) => {
    await syncEngine.enqueue({
      type: 'UPDATE',
      resource: 'stop_arrival',
      data: { routeId, stopId, action: 'arrived', timestamp: new Date().toISOString() },
    });
  };

  const markDeparture = async (routeId: string, stopId: string) => {
    await syncEngine.enqueue({
      type: 'UPDATE',
      resource: 'stop_arrival',
      data: { routeId, stopId, action: 'departed', timestamp: new Date().toISOString() },
    });
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>All Routes</Text>
      </View>

      {showingCached ? (
        <View style={{ backgroundColor: '#FEF3C7', padding: 8, alignItems: 'center' }}>
          <Text style={{ fontSize: 12, color: '#92400E', fontWeight: '500' }}>Showing cached data</Text>
        </View>
      ) : null}

      {pendingSyncCount > 0 ? (
        <View style={{ backgroundColor: '#DBEAFE', padding: 8, alignItems: 'center' }}>
          <Text style={{ fontSize: 12, color: '#1E40AF', fontWeight: '500' }}>
            {pendingSyncCount} stop update{pendingSyncCount > 1 ? 's' : ''} pending sync
          </Text>
        </View>
      ) : null}

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

              {route.stops && route.stops.length > 0 && (
                <View style={{ marginTop: 12, borderTopWidth: 1, borderTopColor: '#F1F5F9', paddingTop: 12 }}>
                  <Text style={{ fontSize: 13, fontWeight: '600', color: theme.colors.text, marginBottom: 8 }}>Stops</Text>
                  {route.stops.map((stop: any, idx: number) => (
                    <View key={stop.id || idx} style={{ flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingVertical: 6 }}>
                      <View style={{ flexDirection: 'row', alignItems: 'center', flex: 1 }}>
                        <View style={{ width: 24, height: 24, borderRadius: 12, backgroundColor: '#EEF2FF', justifyContent: 'center', alignItems: 'center', marginRight: 8 }}>
                          <Text style={{ fontSize: 11, fontWeight: '600', color: theme.colors.primary }}>{idx + 1}</Text>
                        </View>
                        <Text style={{ fontSize: 13, color: theme.colors.text }}>{stop.name}</Text>
                      </View>
                      <View style={{ flexDirection: 'row', gap: 4 }}>
                        <TouchableOpacity
                          onPress={() => markArrival(route.id, stop.id)}
                          style={{ paddingHorizontal: 10, paddingVertical: 4, backgroundColor: '#D1FAE5', borderRadius: 8 }}
                        >
                          <Text style={{ fontSize: 11, color: theme.colors.primary, fontWeight: '500' }}>Arrive</Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                          onPress={() => markDeparture(route.id, stop.id)}
                          style={{ paddingHorizontal: 10, paddingVertical: 4, backgroundColor: '#FEE2E2', borderRadius: 8 }}
                        >
                          <Text style={{ fontSize: 11, color: theme.colors.danger, fontWeight: '500' }}>Depart</Text>
                        </TouchableOpacity>
                      </View>
                    </View>
                  ))}
                </View>
              )}
            </View>
          ))
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
