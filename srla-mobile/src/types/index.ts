export interface User {
  id: number;
  name: string;
  email: string;
  phone?: string;
  insurance_provider?: string;
  insurance_policy?: string;
}

export interface Appointment {
  id: number;
  date: string;
  time: string;
  provider: string;
  type: string;
  status: string;
}

export interface Membership {
  active: boolean;
  plan?: string;
  expires?: string;
}

export interface ChatMessage {
  id: string;
  sender: 'user' | 'bot';
  message: string;
  timestamp: Date;
}

export interface AuthResponse {
  token: string;
  user: User;
}
