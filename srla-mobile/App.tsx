import 'react-native-gesture-handler';
import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import LoginScreen from './src/screens/LoginScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import AppointmentsScreen from './src/screens/AppointmentsScreen';
import MembershipScreen from './src/screens/MembershipScreen';
import ChatScreen from './src/screens/ChatScreen';

const Stack = createStackNavigator();

export default function App() {
  return (
    <SafeAreaProvider>
      <NavigationContainer>
        <Stack.Navigator initialRouteName="Login">
          <Stack.Screen 
            name="Login" 
            component={LoginScreen} 
            options={{ headerShown: false }}
          />
          <Stack.Screen 
            name="Dashboard" 
            component={DashboardScreen} 
            options={{ 
              title: 'SRLA Dashboard',
              headerStyle: {
                backgroundColor: '#2563eb',
              },
              headerTintColor: '#fff',
            }}
          />
          <Stack.Screen 
            name="Appointments" 
            component={AppointmentsScreen} 
            options={{ 
              title: 'My Appointments',
              headerStyle: {
                backgroundColor: '#2563eb',
              },
              headerTintColor: '#fff',
            }}
          />
          <Stack.Screen 
            name="Membership" 
            component={MembershipScreen} 
            options={{ 
              title: 'Recovery Lounge',
              headerStyle: {
                backgroundColor: '#2563eb',
              },
              headerTintColor: '#fff',
            }}
          />
          <Stack.Screen 
            name="Chat" 
            component={ChatScreen} 
            options={{ 
              title: 'Support Chat',
              headerStyle: {
                backgroundColor: '#2563eb',
              },
              headerTintColor: '#fff',
            }}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </SafeAreaProvider>
  );
}
