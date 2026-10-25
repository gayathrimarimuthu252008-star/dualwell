import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from '../api/client';
import { useAuth } from './AuthContext';

export interface Reminder {
  id: number;
  user_id: number;
  title: string;
  message: string;
  category: string;
  scheduled_time: string;
  is_read: boolean;
  is_dismissed: boolean;
  created_at: string;
}

interface NotificationContextType {
  reminders: Reminder[];
  unreadCount: number;
  quietHoursActive: boolean;
  fetchReminders: () => Promise<void>;
  markAsRead: (id: number) => Promise<void>;
  dismissReminder: (id: number) => Promise<void>;
}

const NotificationContext = createContext<NotificationContextType | undefined>(undefined);

export const NotificationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [unreadCount, setUnreadCount] = useState<number>(0);
  const [quietHoursActive, setQuietHoursActive] = useState<boolean>(false);

  const fetchReminders = async () => {
    if (!isAuthenticated) return;
    try {
      const res = await apiClient.get('/notifications/reminders');
      setReminders(res.data.reminders || []);
      setUnreadCount(res.data.unread_count || 0);
      setQuietHoursActive(res.data.quiet_hours_active || false);
    } catch (err) {
      console.error('Failed to fetch reminders', err);
    }
  };

  useEffect(() => {
    if (isAuthenticated) {
      fetchReminders();
      const interval = setInterval(fetchReminders, 60000); // refresh every minute
      return () => clearInterval(interval);
    }
  }, [isAuthenticated]);

  const markAsRead = async (id: number) => {
    try {
      await apiClient.post(`/notifications/reminders/${id}/read`);
      setReminders((prev) =>
        prev.map((r) => (r.id === id ? { ...r, is_read: true } : r))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to mark reminder as read', err);
    }
  };

  const dismissReminder = async (id: number) => {
    try {
      await apiClient.post(`/notifications/reminders/${id}/dismiss`);
      setReminders((prev) => prev.filter((r) => r.id !== id));
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch (err) {
      console.error('Failed to dismiss reminder', err);
    }
  };

  return (
    <NotificationContext.Provider
      value={{
        reminders,
        unreadCount,
        quietHoursActive,
        fetchReminders,
        markAsRead,
        dismissReminder,
      }}
    >
      {children}
    </NotificationContext.Provider>
  );
};

export const useNotifications = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within a NotificationProvider');
  }
  return context;
};
