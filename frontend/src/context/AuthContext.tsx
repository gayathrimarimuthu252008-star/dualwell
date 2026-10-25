import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';

export interface User {
  id: number;
  email: string;
  full_name: string;
  is_active: boolean;
  created_at: string;
}

export interface StudentProfile {
  id: number;
  user_id: number;
  age_range: string;
  major: string;
  primary_sport: string;
  usual_sleep_target_hours: number;
  usual_bedtime: string;
  usual_wake_time: string;
  daily_hydration_goal_ml: number;
  training_days_per_week: number;
  academic_goals: string;
}

interface AuthContextType {
  user: User | null;
  profile: StudentProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName: string) => Promise<void>;
  logout: () => void;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<StudentProfile | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('dualwell_token'));
  const [loading, setLoading] = useState<boolean>(true);

  const fetchProfile = async () => {
    try {
      const res = await apiClient.get('/auth/profile');
      setProfile(res.data);
    } catch (err) {
      console.error('Failed to fetch student profile', err);
    }
  };

  const initAuth = async () => {
    const savedToken = localStorage.getItem('dualwell_token');
    if (savedToken) {
      try {
        const res = await apiClient.get('/auth/me');
        setUser(res.data);
        await fetchProfile();
      } catch (err) {
        console.error('Authentication check failed', err);
        localStorage.removeItem('dualwell_token');
        localStorage.removeItem('dualwell_refresh_token');
        setUser(null);
        setToken(null);
      }
    }
    setLoading(false);
  };

  useEffect(() => {
    initAuth();

    const handleAuthExpired = () => {
      setUser(null);
      setToken(null);
    };

    window.addEventListener('auth_expired', handleAuthExpired);
    return () => window.removeEventListener('auth_expired', handleAuthExpired);
  }, []);

  const login = async (email: string, password: string) => {
    const res = await apiClient.post('/auth/login', { email, password });
    const { access_token, refresh_token, user: loggedUser } = res.data;
    localStorage.setItem('dualwell_token', access_token);
    if (refresh_token) localStorage.setItem('dualwell_refresh_token', refresh_token);
    setToken(access_token);
    setUser(loggedUser);
    await fetchProfile();
  };

  const register = async (email: string, password: string, fullName: string) => {
    const res = await apiClient.post('/auth/register', {
      email,
      password,
      full_name: fullName,
    });
    const { access_token, refresh_token, user: loggedUser } = res.data;
    localStorage.setItem('dualwell_token', access_token);
    if (refresh_token) localStorage.setItem('dualwell_refresh_token', refresh_token);
    setToken(access_token);
    setUser(loggedUser);
    await fetchProfile();
  };

  const logout = () => {
    localStorage.removeItem('dualwell_token');
    localStorage.removeItem('dualwell_refresh_token');
    setUser(null);
    setProfile(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        token,
        isAuthenticated: !!user,
        loading,
        login,
        register,
        logout,
        refreshProfile: fetchProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
