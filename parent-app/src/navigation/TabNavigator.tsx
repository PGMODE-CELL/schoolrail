import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Feather } from '@expo/vector-icons';
import { theme } from '../theme';
import { styles } from '../styles';
import { HomeScreen } from '../screens/HomeScreen';
import { LiveTrackingScreen } from '../screens/LiveTrackingScreen';
import { AttendanceScreen } from '../screens/AttendanceScreen';
import { FeesScreen } from '../screens/FeesScreen';
import { ProfileScreen } from '../screens/ProfileScreen';

const Tab = createBottomTabNavigator();

const HomeStack = createNativeStackNavigator();
function HomeStackScreen() {
  return (
    <HomeStack.Navigator screenOptions={{ headerShown: false }}>
      <HomeStack.Screen name="HomeMain" component={HomeScreen} />
    </HomeStack.Navigator>
  );
}

const TrackStack = createNativeStackNavigator();
function TrackStackScreen() {
  return (
    <TrackStack.Navigator screenOptions={{ headerShown: false }}>
      <TrackStack.Screen name="TrackMain" component={LiveTrackingScreen} />
    </TrackStack.Navigator>
  );
}

const AttendanceStack = createNativeStackNavigator();
function AttendanceStackScreen() {
  return (
    <AttendanceStack.Navigator screenOptions={{ headerShown: false }}>
      <AttendanceStack.Screen name="AttendanceMain" component={AttendanceScreen} />
    </AttendanceStack.Navigator>
  );
}

const FeesStack = createNativeStackNavigator();
function FeesStackScreen() {
  return (
    <FeesStack.Navigator screenOptions={{ headerShown: false }}>
      <FeesStack.Screen name="FeesMain" component={FeesScreen} />
    </FeesStack.Navigator>
  );
}

const ProfileStack = createNativeStackNavigator();
function ProfileStackScreen() {
  return (
    <ProfileStack.Navigator screenOptions={{ headerShown: false }}>
      <ProfileStack.Screen name="ProfileMain" component={ProfileScreen} />
    </ProfileStack.Navigator>
  );
}

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
        component={HomeStackScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Feather name="home" size={size} color={color} />
        }}
      />
      <Tab.Screen
        name="Track"
        component={TrackStackScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Feather name="map-pin" size={size} color={color} />
        }}
      />
      <Tab.Screen
        name="Attendance"
        component={AttendanceStackScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Feather name="calendar" size={size} color={color} />
        }}
      />
      <Tab.Screen
        name="Fees"
        component={FeesStackScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Feather name="dollar-sign" size={size} color={color} />
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileStackScreen}
        options={{
          tabBarIcon: ({ color, size }) => <Feather name="user" size={size} color={color} />
        }}
      />
    </Tab.Navigator>
  );
}
