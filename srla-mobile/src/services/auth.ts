import AsyncStorage from '@react-native-async-storage/async-storage';
import api from './api';
import { AuthResponse, User } from '../types';

export const authService = {
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await api.post<AuthResponse>('/auth/login', {
      email,
      password,
    });
    
    await AsyncStorage.setItem('authToken', response.data.token);
    await AsyncStorage.setItem('currentUser', JSON.stringify(response.data.user));
    
    return response.data;
  },

  async register(userData: {
    name: string;
    email: string;
    password: string;
    phone?: string;
    insurance_provider?: string;
    insurance_policy?: string;
  }): Promise<void> {
    await api.post('/auth/register', userData);
  },

  async logout(): Promise<void> {
    await AsyncStorage.removeItem('authToken');
    await AsyncStorage.removeItem('currentUser');
  },

  async getCurrentUser(): Promise<User | null> {
    const userStr = await AsyncStorage.getItem('currentUser');
    return userStr ? JSON.parse(userStr) : null;
  },

  async getToken(): Promise<string | null> {
    return await AsyncStorage.getItem('authToken');
  },

  async isAuthenticated(): Promise<boolean> {
    const token = await AsyncStorage.getItem('authToken');
    return !!token;
  },
};
