import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import api from '../services/api';
import { authService } from '../services/auth';
import { User, Appointment, Membership } from '../types';

const DashboardScreen = ({ navigation }: any) => {
  const [user, setUser] = useState<User | null>(null);
  const [nextAppointment, setNextAppointment] = useState<Appointment | null>(null);
  const [membership, setMembership] = useState<Membership | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);

      const [appointmentRes, membershipRes] = await Promise.all([
        api.get('/appointments/next'),
        api.get('/membership/status'),
      ]);

      setNextAppointment(appointmentRes.data);
      setMembership(membershipRes.data);
    } catch (error) {
      console.error('Dashboard load error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadDashboardData();
  };

  const handleLogout = async () => {
    await authService.logout();
    navigation.replace('Login');
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#2563eb" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        <View style={styles.header}>
          <Text style={styles.greeting}>Welcome back,</Text>
          <Text style={styles.userName}>{user?.name || 'Patient'}</Text>
        </View>

        <View style={styles.cardsContainer}>
          {/* Next Appointment Card */}
          <TouchableOpacity
            style={styles.card}
            onPress={() => navigation.navigate('Appointments')}
          >
            <Text style={styles.cardTitle}>Next Appointment</Text>
            {nextAppointment ? (
              <>
                <Text style={styles.cardMainText}>{nextAppointment.date}</Text>
                <Text style={styles.cardSubText}>{nextAppointment.time}</Text>
                <Text style={styles.cardSubText}>with {nextAppointment.provider}</Text>
              </>
            ) : (
              <Text style={styles.cardSubText}>No upcoming appointments</Text>
            )}
          </TouchableOpacity>

          {/* Membership Card */}
          <TouchableOpacity
            style={styles.card}
            onPress={() => navigation.navigate('Membership')}
          >
            <Text style={styles.cardTitle}>Recovery Lounge</Text>
            {membership?.active ? (
              <>
                <Text style={styles.cardMainText}>Active Member</Text>
                <Text style={styles.cardSubText}>Tap to view benefits</Text>
              </>
            ) : (
              <>
                <Text style={styles.cardMainText}>Join Today</Text>
                <Text style={styles.cardSubText}>$100/month</Text>
              </>
            )}
          </TouchableOpacity>

          {/* Quick Actions */}
          <View style={styles.quickActions}>
            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Appointments')}
            >
              <Text style={styles.actionButtonText}>Book Appointment</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.actionButton}
              onPress={() => navigation.navigate('Chat')}
            >
              <Text style={styles.actionButtonText}>Chat Support</Text>
            </TouchableOpacity>
          </View>

          {/* Insurance Info */}
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Insurance Information</Text>
            <Text style={styles.cardSubText}>
              Provider: {user?.insurance_provider || 'Not specified'}
            </Text>
            <Text style={styles.cardSubText}>
              Policy: {user?.insurance_policy || 'Not specified'}
            </Text>
          </View>
        </View>

        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>Logout</Text>
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f3f4f6',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  header: {
    padding: 24,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  greeting: {
    fontSize: 16,
    color: '#6b7280',
  },
  userName: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    marginTop: 4,
  },
  cardsContainer: {
    padding: 16,
  },
  card: {
    backgroundColor: 'white',
    padding: 20,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 12,
  },
  cardMainText: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2563eb',
    marginBottom: 4,
  },
  cardSubText: {
    fontSize: 16,
    color: '#6b7280',
    marginTop: 4,
  },
  quickActions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  actionButton: {
    flex: 1,
    backgroundColor: '#2563eb',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginHorizontal: 4,
  },
  actionButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
  logoutButton: {
    margin: 16,
    padding: 16,
    backgroundColor: '#ef4444',
    borderRadius: 8,
    alignItems: 'center',
  },
  logoutButtonText: {
    color: 'white',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default DashboardScreen;
