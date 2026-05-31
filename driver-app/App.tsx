import React, { useState, useEffect } from 'react';
import { View, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthContext } from './src/context/AuthContext';
import { TabNavigator } from './src/navigation/TabNavigator';
import { LoginScreen } from './src/screens/LoginScreen';

export default function App() {
  const [authState, setAuthState] = useState<{ token: string; user: any } | null>(null);
  const [initializing, setInitializing] = useState(true);

  useEffect(() => {
    AsyncStorage.getItem('token').then(t => {
      if (t) {
        AsyncStorage.getItem('user').then(u => {
          if (u) setAuthState({ token: t, user: JSON.parse(u) });
          setInitializing(false);
        });
      } else {
        setInitializing(false);
      }
    });
  }, []);

  if (initializing) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#F8FAFC' }}>
        <ActivityIndicator size="large" color="#10B981" />
      </View>
    );
  }

  if (!authState) {
    return <LoginScreen onLogin={(token, user) => setAuthState({ token, user })} />;
  }

  const logout = async () => {
    await AsyncStorage.multiRemove(['token', 'user']);
    setAuthState(null);
  };

  return (
    <AuthContext.Provider value={{ user: authState.user, token: authState.token, logout }}>
      <NavigationContainer>
        <TabNavigator />
      </NavigationContainer>
    </AuthContext.Provider>
  );
}
