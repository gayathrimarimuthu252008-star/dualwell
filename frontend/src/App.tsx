import React, { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { NotificationProvider } from './context/NotificationContext';
import { Sidebar, NavTab } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { AuthPage } from './pages/AuthPage';

import { DashboardPage } from './pages/DashboardPage';
import { WearableMonitoringPage } from './pages/WearableMonitoringPage';
import { AcademicCalendarPage } from './pages/AcademicCalendarPage';
import { SmartSchedulerPage } from './pages/SmartSchedulerPage';
import { NutritionHydrationPage } from './pages/NutritionHydrationPage';
import { SleepRecoveryPage } from './pages/SleepRecoveryPage';
import { RecoveryGuidePage } from './pages/RecoveryGuidePage';
import { PriorityRescueModePage } from './pages/PriorityRescueModePage';
import { WeeklyInsightsPage } from './pages/WeeklyInsightsPage';
import { PrivacySettingsPage } from './pages/PrivacySettingsPage';
import apiClient from './api/client';

const MainApp: React.FC = () => {
  const { isAuthenticated, loading } = useAuth();
  const [activeTab, setActiveTab] = useState<NavTab>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [currentRiskLevel, setCurrentRiskLevel] = useState<'GREEN' | 'YELLOW' | 'RED'>('YELLOW');

  useEffect(() => {
    if (isAuthenticated) {
      const fetchRisk = async () => {
        try {
          const res = await apiClient.get('/load-risk/current');
          setCurrentRiskLevel(res.data.risk_level || 'YELLOW');
        } catch (err) {
          console.error('Failed to load risk status in Header:', err);
        }
      };
      fetchRisk();
      const interval = setInterval(fetchRisk, 120000); // refresh every 2 mins
      return () => clearInterval(interval);
    }
  }, [isAuthenticated, activeTab]);

  if (loading) {
    return (
      <div className="min-h-screen bg-dualbg flex items-center justify-center">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-12 h-12 rounded-2xl bg-primary flex items-center justify-center text-white font-bold text-xl shadow-md animate-pulse">
            DW
          </div>
          <span className="text-xs font-semibold text-dualtext-secondary">
            Loading DualWell Student System...
          </span>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <AuthPage />;
  }

  const renderActiveScreen = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardPage setActiveTab={setActiveTab} />;
      case 'wearable':
        return <WearableMonitoringPage />;
      case 'calendar':
        return <AcademicCalendarPage />;
      case 'scheduler':
        return <SmartSchedulerPage />;
      case 'nutrition':
        return <NutritionHydrationPage />;
      case 'sleep':
        return <SleepRecoveryPage />;
      case 'recovery':
        return <RecoveryGuidePage />;
      case 'rescue':
        return <PriorityRescueModePage />;
      case 'insights':
        return <WeeklyInsightsPage />;
      case 'privacy':
        return <PrivacySettingsPage />;
      default:
        return <DashboardPage setActiveTab={setActiveTab} />;
    }
  };

  return (
    <div className="min-h-screen bg-dualbg flex">
      {/* Sidebar */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-64">
        {/* Header */}
        <Header
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
          setActiveTab={setActiveTab}
          currentRiskLevel={currentRiskLevel}
        />

        {/* Dynamic Screen View */}
        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full">
          {renderActiveScreen()}
        </main>
      </div>
    </div>
  );
};

export function App() {
  return (
    <AuthProvider>
      <NotificationProvider>
        <MainApp />
      </NotificationProvider>
    </AuthProvider>
  );
}

export default App;
