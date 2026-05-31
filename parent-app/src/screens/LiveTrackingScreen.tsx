import React, { useState, useEffect, useCallback, useRef } from 'react';
import { View, Text, SafeAreaView, ActivityIndicator, TouchableOpacity } from 'react-native';
import { Feather } from '@expo/vector-icons';
import MapView, { Marker, Polyline } from 'react-native-maps';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { theme } from '../theme';
import { styles } from '../styles';
import { apiRequest, isOnline } from '../config';

const WS_URL = typeof window !== 'undefined'
  ? `ws://${window.location.host}/ws/gps`
  : 'ws://10.0.2.2:3001/ws/gps';

export function LiveTrackingScreen() {
  const [gps, setGps] = useState<any>(null);
  const [routePolyline, setRoutePolyline] = useState<any[]>([]);
  const [stops, setStops] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showingCached, setShowingCached] = useState(false);
  const [lastSeen, setLastSeen] = useState<number | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const pollRef = useRef<NodeJS.Timeout | null>(null);

  const loadCached = useCallback(async () => {
    const cachedGps = await AsyncStorage.getItem('live_gps');
    const cachedPolyline = await AsyncStorage.getItem('live_polyline');
    const cachedStops = await AsyncStorage.getItem('live_stops');
    if (cachedGps) {
      setGps(JSON.parse(cachedGps));
      setLastSeen(Date.now());
    }
    if (cachedPolyline) setRoutePolyline(JSON.parse(cachedPolyline));
    if (cachedStops) setStops(JSON.parse(cachedStops));
  }, []);

  const fetchGps = useCallback(async () => {
    setError('');
    try {
      const d = await apiRequest('/gps/active');
      if (Array.isArray(d) && d.length > 0) {
        setGps(d[0]);
        setLastSeen(Date.now());
        await AsyncStorage.setItem('live_gps', JSON.stringify(d[0]));
      } else {
        setGps(null);
      }
      setShowingCached(false);
    } catch {
      const online = await isOnline();
      if (!online) {
        await loadCached();
        if (gps) setShowingCached(true);
      } else {
        await loadCached();
        if (gps) setShowingCached(true);
        else setError('Failed to fetch GPS data');
      }
    }
    setLoading(false);
  }, []);

  const connectWebSocket = useCallback(() => {
    try {
      const ws = new WebSocket(WS_URL);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.latitude && data.longitude) {
            setGps(data);
            setLastSeen(Date.now());
            AsyncStorage.setItem('live_gps', JSON.stringify(data));
          }
          if (data.route) {
            setRoutePolyline(data.route);
            AsyncStorage.setItem('live_polyline', JSON.stringify(data.route));
          }
          if (data.stops) {
            setStops(data.stops);
            AsyncStorage.setItem('live_stops', JSON.stringify(data.stops));
          }
        } catch {}
      };
      ws.onclose = () => {
        if (pollRef.current) clearInterval(pollRef.current);
        pollRef.current = setInterval(fetchGps, 10000);
      };
      ws.onerror = () => {
        if (pollRef.current) clearInterval(pollRef.current);
        pollRef.current = setInterval(fetchGps, 10000);
      };
      wsRef.current = ws;
    } catch {
      pollRef.current = setInterval(fetchGps, 10000);
    }
  }, [fetchGps]);

  useEffect(() => {
    loadCached().then(() => {
      fetchGps().then(() => {
        connectWebSocket();
      });
    });
    return () => {
      if (wsRef.current) wsRef.current.close();
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

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

  if (error && !showingCached && !gps) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.screenHeader}>
          <Text style={styles.screenTitle}>Live Tracking</Text>
        </View>
        <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', padding: 20 }}>
          <Feather name="alert-circle" size={48} color={theme.colors.danger} />
          <Text style={{ fontSize: 16, color: theme.colors.textSecondary, marginTop: 16, textAlign: 'center' }}>{error}</Text>
          <TouchableOpacity
            onPress={() => { setLoading(true); fetchGps(); }}
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

  const minutesAgo = lastSeen ? Math.round((Date.now() - lastSeen) / 60000) : null;

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.screenHeader}>
        <Text style={styles.screenTitle}>Live Tracking</Text>
      </View>

      {showingCached && minutesAgo !== null ? (
        <View style={{ backgroundColor: '#FEF3C7', padding: 8, alignItems: 'center' }}>
          <Text style={{ fontSize: 12, color: '#92400E', fontWeight: '500' }}>
            Last seen {minutesAgo} min ago
          </Text>
        </View>
      ) : null}

      <View style={styles.mapContainer}>
        <MapView style={{ flex: 1 }} initialRegion={region} region={region}>
          {routePolyline.length > 0 && (
            <Polyline coordinates={routePolyline} strokeColor={theme.colors.primary} strokeWidth={3} />
          )}
          {stops.map((stop: any, idx: number) => (
            <Marker
              key={idx}
              coordinate={{ latitude: stop.latitude, longitude: stop.longitude }}
              title={stop.name || `Stop ${idx + 1}`}
              pinColor="orange"
            />
          ))}
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
