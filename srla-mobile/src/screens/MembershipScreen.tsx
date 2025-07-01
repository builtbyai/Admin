import React, { useEffect, useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import api from '../services/api';
import { Membership } from '../types';

const MembershipScreen = ({ navigation }: any) => {
  const [membership, setMembership] = useState<Membership | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadMembershipStatus();
  }, []);

  const loadMembershipStatus = async () => {
    try {
      const response = await api.get('/membership/status');
      setMembership(response.data);
    } catch (error) {
      console.error('Load membership error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async () => {
    try {
      const response = await api.post('/membership/subscribe', {
        plan: 'recovery-lounge-monthly',
      });
      
      if (response.data.checkoutUrl) {
        // In a real app, you would open this URL in a WebView or browser
        Alert.alert(
          'Subscription',
          'You will be redirected to complete your subscription.',
          [
            { text: 'Cancel', style: 'cancel' },
            { text: 'Continue', onPress: () => console.log('Open checkout URL') },
          ]
        );
      }
    } catch (error) {
      Alert.alert('Error', 'Failed to start subscription process');
    }
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
      <ScrollView>
        <View style={styles.header}>
          <Text style={styles.title}>Recovery Lounge Membership</Text>
          <Text style={styles.price}>$100/month</Text>
        </View>

        {membership?.active ? (
          <View style={styles.activeCard}>
            <Text style={styles.activeText}>✓ Active Member</Text>
            <Text style={styles.expiresText}>
              Renews: {membership.expires ? new Date(membership.expires).toLocaleDateString() : 'Monthly'}
            </Text>
          </View>
        ) : null}

        <View style={styles.benefitsSection}>
          <Text style={styles.sectionTitle}>Member Benefits</Text>
          
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>✓</Text>
            <Text style={styles.benefitText}>Unlimited access to recovery lounge</Text>
          </View>
          
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>✓</Text>
            <Text style={styles.benefitText}>Priority appointment scheduling</Text>
          </View>
          
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>✓</Text>
            <Text style={styles.benefitText}>Exclusive member events and workshops</Text>
          </View>
          
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>✓</Text>
            <Text style={styles.benefitText}>Personalized recovery plans</Text>
          </View>
          
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>✓</Text>
            <Text style={styles.benefitText}>10% discount on additional services</Text>
          </View>
        </View>

        <View style={styles.facilitiesSection}>
          <Text style={styles.sectionTitle}>Recovery Lounge Facilities</Text>
          <Text style={styles.facilityText}>• Compression therapy</Text>
          <Text style={styles.facilityText}>• Cold plunge pools</Text>
          <Text style={styles.facilityText}>• Infrared sauna</Text>
          <Text style={styles.facilityText}>• Recovery boots</Text>
          <Text style={styles.facilityText}>• Stretching area</Text>
          <Text style={styles.facilityText}>• Relaxation zones</Text>
        </View>

        {!membership?.active && (
          <TouchableOpacity style={styles.subscribeButton} onPress={handleSubscribe}>
            <Text style={styles.subscribeButtonText}>Subscribe Now</Text>
          </TouchableOpacity>
        )}

        <View style={styles.termsSection}>
          <Text style={styles.termsText}>
            Cancel anytime. No long-term contracts. Membership includes all recovery lounge amenities during operating hours.
          </Text>
        </View>
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
    backgroundColor: 'white',
    padding: 24,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#e5e7eb',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  price: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#2563eb',
  },
  activeCard: {
    backgroundColor: '#10b981',
    margin: 16,
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  activeText: {
    color: 'white',
    fontSize: 20,
    fontWeight: 'bold',
  },
  expiresText: {
    color: 'white',
    fontSize: 14,
    marginTop: 4,
  },
  benefitsSection: {
    backgroundColor: 'white',
    margin: 16,
    padding: 20,
    borderRadius: 12,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 16,
  },
  benefitItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  benefitIcon: {
    color: '#10b981',
    fontSize: 18,
    fontWeight: 'bold',
    marginRight: 12,
  },
  benefitText: {
    flex: 1,
    fontSize: 16,
    color: '#4b5563',
    lineHeight: 22,
  },
  facilitiesSection: {
    backgroundColor: 'white',
    margin: 16,
    marginTop: 0,
    padding: 20,
    borderRadius: 12,
  },
  facilityText: {
    fontSize: 16,
    color: '#4b5563',
    marginBottom: 8,
    lineHeight: 22,
  },
  subscribeButton: {
    margin: 16,
    padding: 18,
    backgroundColor: '#2563eb',
    borderRadius: 8,
    alignItems: 'center',
  },
  subscribeButtonText: {
    color: 'white',
    fontSize: 18,
    fontWeight: '600',
  },
  termsSection: {
    padding: 20,
  },
  termsText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 20,
  },
});

export default MembershipScreen;
