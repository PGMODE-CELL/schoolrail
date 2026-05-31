import React, { useState, useEffect, useCallback } from 'react';
import { View, Text, SafeAreaView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { Feather } from '@expo/vector-icons';
import MapView, { Marker } from 'react-native-maps';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

export function LiveTrackingScreen() {
  const [gps, setGps] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchGps = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const d = await apiRequest('/gps/active');
      if (Array.isArray(d) && d.length > 0) {
        setGps(d[0]);
      } else {
        setGps(null);
      }
    } catch (e: any) {
      setError(e.message || 'Failed to fetch GPS data');
    }
    setLoading(false);
  }, []);

  useEffect(() => { fetchGps(); }, [fetchGps]);

  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.screenHeader}>
          <Text style={styles.screenTitle}>Live Tracking</Text>
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
          <Text style={styles.screenTitle}>Live Tracking</Text>
        </View>
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
          <Feather name="alert-circle" size={48} color={theme.colors.danger} />
          <Text style={{ fontSize: 16, color: theme.colors.textSecondary, marginTop: 16, textAlign: 'center' }}>{error}</Text>
          <TouchableOpacity
            onPress={fetchGps}
            style={{ marginTop: 16, backgroundColor: theme.colors.primary, borderRadius: 12, paddingHorizontal: 24, paddingVertical: 12 }}
          >
            <Text style={{ color: 'white', fontSize: 14, fontWeight: '600' }}>Retry</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  const region = gps ? {
    latitude: gps.latitude,
    longitude: gps.longitude,
    latitudeDelta: 0.01,
    longitudeDelta: 0.01,
  } : {
    latitude: 20.5937,
    longitude: 78.9629,
    latitudeDelta: 30,
    longitudeDelta: 30,
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Live Tracking</Text>
      </View>
      <View style={styles.mapContainer}>
        <MapView style={{ flex: 1 }} initialRegion={region} region={region}>
          {gps && (
            <Marker
              coordinate={{ latitude: gps.latitude, longitude: gps.longitude }}
              title="Vehicle"
              description={`Speed: ${gps.speed || 0} km/h`}
            />
          )}
        </MapView>
      </View>
      <View style={styles.trackingInfo}>
        <View style={styles.trackingDetail}>
          <Text style={styles.trackingLabel}>Current Stop</Text>
          <Text style={styles.trackingValue}>{gps?.current_stop || 'N/A'}</Text>
        </View>
        <View style={styles.trackingDetail}>
          <Text style={styles.trackingLabel}>Speed</Text>
          <Text style={styles.trackingValue}>{gps?.speed || 0} km/h</Text>
        </View>
        <View style={styles.trackingDetail}>
          <Text style={styles.trackingLabel}>Location</Text>
          <Text style={styles.trackingValue}>{gps ? `${gps.latitude?.toFixed(4)}, ${gps.longitude?.toFixed(4)}` : 'N/A'}</Text>
        </View>
      </View>
    </SafeAreaView>
  );
}
