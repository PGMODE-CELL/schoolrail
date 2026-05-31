import React, { useState, useEffect } from 'react';
import { View, Text, SafeAreaView } from 'react-native';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest } from '../config';

export function LiveTrackingScreen() {
  const [gps, setGps] = useState<any>(null);
  const [gpsList, setGpsList] = useState<any[]>([]);

  useEffect(() => {
    apiRequest('/gps/active').then(d => {
      if (d?.length) { setGpsList(d); setGps(d[0]); }
    }).catch(() => {
      setGps({ vehicle_id: '1', latitude: 28.6139, longitude: 77.2090, speed: 35, last_updated: new Date().toISOString() });
    });
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Live Tracking</Text>
      </View>
      <View style={styles.mapContainer}>
        <View style={styles.mapPlaceholder}>
          <Feather name="map" size={48} color={theme.colors.textSecondary} />
          <Text style={styles.mapText}>Map View</Text>
          <Text style={styles.mapSubtext}>Real-time tracking enabled</Text>
        </View>
      </View>
      <View style={styles.trackingInfo}>
        <View style={styles.trackingDetail}>
          <Text style={styles.trackingLabel}>Current Stop</Text>
          <Text style={styles.trackingValue}>Stop 5 - Sector 12</Text>
        </View>
        <View style={styles.trackingDetail}>
          <Text style={styles.trackingLabel}>Speed</Text>
          <Text style={styles.trackingValue}>{gps?.speed || 35} km/h</Text>
        </View>
        <View style={styles.trackingDetail}>
          <Text style={styles.trackingLabel}>Location</Text>
          <Text style={styles.trackingValue}>{gps ? `${gps.latitude?.toFixed(4)}, ${gps.longitude?.toFixed(4)}` : '28.6139, 77.2090'}</Text>
        </View>
      </View>
    </SafeAreaView>
  );
}
