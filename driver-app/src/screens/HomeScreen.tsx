import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, SafeAreaView } from 'react-native';
import { useNavigation } from '@react-navigation/native';
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

export function HomeScreen() {
  const navigation = useNavigation();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [routes, setRoutes] = useState<any[]>([]);

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    apiRequest('/routes').then(d => { if (d?.length) setRoutes(d); }).catch(() => {});
  }, []);

  const displayRoutes = routes.length > 0 ? routes : mockRoutes;
  const todayTrips = displayRoutes.filter((r: any) => r.status === 'active' || r.status === 'Active').length;
  const totalStudents = displayRoutes.reduce((acc: number, r: any) => acc + (r.student_count || (r.stops ? r.stops.length : 0) || r.students || 0), 0);

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView showsVerticalScrollIndicator={false}>
        <View style={[styles.header, { backgroundColor: theme.colors.primary }]}>
          <View style={styles.headerTop}>
            <View>
              <Text style={styles.greeting}>Good Morning!</Text>
              <Text style={styles.driverName}>Driver John</Text>
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
              <Text style={styles.statValue}>8</Text>
              <Text style={styles.statLabel}>Stops</Text>
            </View>
          </View>
        </View>

        <View style={styles.content}>
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>My Routes Today</Text>
            {displayRoutes.slice(0, 2).map((route: any) => (
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
            ))}
          </View>

          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Quick Actions</Text>
            <View style={styles.actionsGrid}>
              <TouchableOpacity style={styles.actionButton}>
                <View style={[styles.actionIcon, { backgroundColor: '#ECFDF5' }]}>
                  <Feather name="check-circle" size={24} color={theme.colors.primary} />
                </View>
                <Text style={styles.actionLabel}>Take Attendance</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionButton}>
                <View style={[styles.actionIcon, { backgroundColor: '#EEF2FF' }]}>
                  <Feather name="navigation" size={24} color={theme.colors.primary} />
                </View>
                <Text style={styles.actionLabel}>Start Trip</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.actionButton}>
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
