import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { HomeScreen } from '../screens/HomeScreen';
import { LiveTrackingScreen } from '../screens/LiveTrackingScreen';
import { AttendanceScreen } from '../screens/AttendanceScreen';
import { FeesScreen } from '../screens/FeesScreen';
import { ProfileScreen } from '../screens/ProfileScreen';

const Tab = createBottomTabNavigator();

export function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarStyle: styles.tabBar,
        tabBarActiveTintColor: theme.colors.primary,
        tabBarInactiveTintColor: theme.colors.textSecondary,
      }}
    >
      <Tab.Screen 
        name="Home" 
        component={HomeScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Feather name="home" size={size} color={color} />
        }}
      />
      <Tab.Screen 
        name="Track" 
        component={LiveTrackingScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Feather name="map-pin" size={size} color={color} />
        }}
      />
      <Tab.Screen 
        name="Attendance" 
        component={AttendanceScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Feather name="calendar" size={size} color={color} />
        }}
      />
      <Tab.Screen 
        name="Fees" 
        component={FeesScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Feather name="dollar-sign" size={size} color={color} />
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Feather name="user" size={size} color={color} />
        }}
      />
    </Tab.Navigator>
  );
}
