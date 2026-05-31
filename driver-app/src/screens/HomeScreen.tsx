import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView, ActivityIndicator } from 'react-native';
import { useNavigation } from '@react-navigation/native';
import { Feather } from '@expo/vector-icons';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest, isOnline } from '../config';
import { useAuth } from '../context/AuthContext';

export function HomeScreen() {
  const navigation = useNavigation();
  const { user, isOffline } = useAuth();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [routes, setRoutes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showingCached, setShowingCached] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const fetchRoutes = async () => {
    setLoading(true);
    setError('');
    setShowingCached(false);

    const online = await isOnline();
    if (!online) {
      const cached = await AsyncStorage.getItem('driver_home_routes');
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
        await AsyncStorage.setItem('driver_home_routes', JSON.stringify(d));
      }
    } catch {
      const cached = await AsyncStorage.getItem('driver_home_routes');
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

  const todayTrips = routes.filter((r: any) => r.status === 'active' || r.status === 'Active').length;
  const totalStudents = routes.reduce((acc: number, r: any) => acc + (r.student_count || (r.stops ? r.stops.length : 0) || r.students || 0), 0);
  const totalStops = routes.reduce((acc: number, r: any) => acc + (r.stop_count || (r.stops ? r.stops.length : 0) || 0), 0);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        {isOffline || showingCached ? (
          <View style={{ backgroundColor: '#FEF3C7', padding: 8, alignItems: 'center' }}>
            <Text style={{ fontSize: 12, color: '#92400E', fontWeight: '500' }}>
              {isOffline ? 'You are offline' : 'Showing cached data'}
            </Text>
          </View>
        ) : null}

        <View style={[styles.header, { backgroundColor: theme.colors.primary }]}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.greeting}>Good Morning!</Text>
              <Text style={styles.driverName}>{user?.full_name || 'Driver'}</Text>
            </View>
            <View style={styles.timeContainer}>
              <Text style={styles.time}>{currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Text>
              <Text style={styles.date}>{currentTime.toLocaleDateString()}</Text>
            </View>
          </View>

          <View style={styles.statsContainer}>
            <View style={styles.statBox}>
              <Text style={styles.statValue}>{todayTrips}</Text>
              <Text style={styles.statLabel}>Active Routes</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statValue}>{totalStudents}</Text>
              <Text style={styles.statLabel}>Students</Text>
            </View>
            <View style={styles.statBox}>
              <Text style={styles.statValue}>{totalStops}</Text>
              <Text style={styles.statLabel}>Stops</Text>
            </View>
          </View>
        </View>

        <View style={styles.content}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>My Routes Today</Text>
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
                <Text style={{ color: theme.colors.textSecondary, marginTop: 12 }}>No route assigned</Text>
              </View>
            ) : (
              routes.slice(0, 2).map((route: any) => (
                <TouchableOpacity key={route.id} style={styles.routeCard}>
                  <View style={styles.routeHeader}>
                    <View style={[styles.routeStatus, { backgroundColor: (route.status === 'active' || route.status === 'Active') ? '#D1FAE5' : '#FEF3C7' }]}>
                      <View style={[styles.statusDot, { backgroundColor: (route.status === 'active' || route.status === 'Active') ? theme.colors.primary : theme.colors.warning }]} />
                      <Text style={[styles.statusText, { color: (route.status === 'active' || route.status === 'Active') ? theme.colors.primary : theme.colors.warning }]}>
                        {typeof route.status === 'string' ? route.status.charAt(0).toUpperCase() + route.status.slice(1) : 'Active'}
                      </Text>
                    </View>
                    <Feather name="chevron-right" size={20} color={theme.colors.textSecondary} />
                  </View>
                  <Text style={styles.routeName}>{route.name}</Text>
                  <View style={styles.routeDetails}>
                    <View style={styles.routeDetail}>
                      <Feather name="users" size={14} color={theme.colors.textSecondary} />
                      <Text style={styles.routeDetailText}>{route.students || route.student_count || 0} students</Text>
                    </View>
                    <View style={styles.routeDetail}>
                      <Feather name="map-pin" size={14} color={theme.colors.textSecondary} />
                      <Text style={styles.routeDetailText}>{route.stops || route.stop_count || 0} stops</Text>
                    </View>
                    <View style={styles.routeDetail}>
                      <Feather name="truck" size={14} color={theme.colors.textSecondary} />
                      <Text style={styles.routeDetailText}>{route.vehicle || route.vehicle_name || ''}</Text>
                    </View>
                  </View>
                </TouchableOpacity>
              ))
            )}
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Quick Actions</Text>
            <View style={styles.actionsGrid}>
              <TouchableOpacity style={styles.actionButton} onPress={() => navigation.navigate('Attendance')}>
                <View style={[styles.actionIcon, { backgroundColor: '#ECFDF5' }]}>
                  <Feather name="check-circle" size={24} color={theme.colors.primary} />
                </View>
                <Text style={styles.actionLabel}>Take Attendance</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionButton} onPress={() => navigation.navigate('Routes')}>
                <View style={[styles.actionIcon, { backgroundColor: '#EEF2FF' }]}>
                  <Feather name="navigation" size={24} color={theme.colors.primary} />
                </View>
                <Text style={styles.actionLabel}>View Routes</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionButton} onPress={() => navigation.navigate('Vehicle')}>
                <View style={[styles.actionIcon, { backgroundColor: '#FEF3C7' }]}>
                  <Feather name="alert-circle" size={24} color={theme.colors.warning} />
                </View>
                <Text style={styles.actionLabel}>Report Issue</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionButton}>
                <View style={[styles.actionIcon, { backgroundColor: '#FCE7F3' }]}>
                  <Feather name="message-circle" size={24} color="#EC4899" />
                </View>
                <Text style={styles.actionLabel}>Message</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
