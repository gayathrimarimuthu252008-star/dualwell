import React, { useState, useRef, useEffect } from 'react';
import {
  Menu,
  Bell,
  LifeBuoy,
  LogOut,
  Moon,
  Clock,
  CheckCircle,
  AlertTriangle
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useNotifications } from '../../context/NotificationContext';
import { NavTab } from './Sidebar';

interface HeaderProps {
  onToggleSidebar: () => void;
  setActiveTab: (tab: NavTab) => void;
  currentRiskLevel?: 'GREEN' | 'YELLOW' | 'RED';
}

export const Header: React.FC<HeaderProps> = ({
  onToggleSidebar,
  setActiveTab,
  currentRiskLevel = 'YELLOW',
}) => {
  const { user, profile, logout } = useAuth();
  const { reminders, unreadCount, quietHoursActive, markAsRead, dismissReminder } = useNotifications();
  const [showNotifications, setShowNotifications] = useState(false);
  const notifRef = useRef<HTMLDivElement>(null);

  // Close notifications dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notifRef.current && !notifRef.current.contains(event.target as Node)) {
        setShowNotifications(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const todayStr = new Date().toLocaleDateString('en-US', {
    weekday: 'long',
    month: 'short',
    day: 'numeric',
  });

  const getRiskBadge = () => {
    switch (currentRiskLevel) {
      case 'GREEN':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-mint text-risk-green border border-emerald-200">
            <span className="w-2 h-2 rounded-full bg-risk-green animate-pulse" />
            <span>Optimal Recovery</span>
          </span>
        );
      case 'YELLOW':
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-cream text-risk-yellow border border-amber-200">
            <span className="w-2 h-2 rounded-full bg-risk-yellow animate-pulse" />
            <span>Elevated Load</span>
          </span>
        );
      case 'RED':
      default:
        return (
          <span className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-red-100 text-risk-red border border-red-200">
            <span className="w-2 h-2 rounded-full bg-risk-red animate-ping" />
            <span>Overload Triage</span>
          </span>
        );
    }
  };

  return (
    <header className="h-16 bg-white border-b border-bordercolor sticky top-0 z-30 flex items-center justify-between px-4 sm:px-6">
      {/* Left: Mobile hamburger & Today date */}
      <div className="flex items-center space-x-4">
        <button
          onClick={onToggleSidebar}
          className="p-2 rounded-lg text-dualtext-secondary hover:bg-dualbg lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>

        <div>
          <h1 className="text-sm sm:text-base font-semibold text-dualtext-primary">
            Hello, {user?.full_name?.split(' ')[0] || 'Athlete'} 👋
          </h1>
          <p className="text-xs text-dualtext-secondary">{todayStr}</p>
        </div>
      </div>

      {/* Right controls */}
      <div className="flex items-center space-x-3 sm:space-x-4">
        {/* Risk badge indicator */}
        <div className="hidden sm:block">
          {getRiskBadge()}
        </div>

        {/* Priority Rescue Mode quick button */}
        <button
          onClick={() => setActiveTab('rescue')}
          className="flex items-center space-x-1.5 bg-risk-red/10 hover:bg-risk-red/20 text-risk-red text-xs sm:text-sm font-semibold px-3 py-1.5 rounded-xl border border-risk-red/20 transition-colors"
          title="Activate Priority Rescue Mode"
        >
          <LifeBuoy className="w-4 h-4 animate-spin-slow" />
          <span className="hidden md:inline">Rescue Mode</span>
        </button>

        {/* In-app Notification Bell Dropdown */}
        <div className="relative" ref={notifRef}>
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="p-2 rounded-xl text-dualtext-secondary hover:bg-dualbg relative transition-colors"
            title="In-App Alarms & Reminders"
          >
            <Bell className="w-5 h-5" />
            {unreadCount > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 rounded-full bg-primary text-white text-[10px] font-bold flex items-center justify-center">
                {unreadCount}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white rounded-2xl shadow-xl border border-bordercolor overflow-hidden z-50">
              <div className="p-4 border-b border-bordercolor flex items-center justify-between bg-dualbg/50">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-sm text-dualtext-primary">
                    Smart Alarms & Reminders
                  </span>
                  {quietHoursActive && (
                    <span className="text-[10px] bg-slate-200 text-dualtext-secondary px-2 py-0.5 rounded-full flex items-center space-x-1">
                      <Moon className="w-3 h-3" />
                      <span>Quiet Hours</span>
                    </span>
                  )}
                </div>
                <span className="text-xs text-dualtext-secondary">
                  {unreadCount} unread
                </span>
              </div>

              <div className="max-h-80 overflow-y-auto divide-y divide-bordercolor">
                {reminders.length === 0 ? (
                  <div className="p-6 text-center text-xs text-dualtext-secondary">
                    No active reminders right now. All caught up!
                  </div>
                ) : (
                  reminders.map((rem) => (
                    <div
                      key={rem.id}
                      className={`p-3.5 hover:bg-dualbg/50 transition-colors ${
                        !rem.is_read ? 'bg-primary-soft/30' : ''
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-2">
                          <span className="text-[10px] font-bold tracking-wider uppercase px-2 py-0.5 rounded bg-white border border-bordercolor text-dualtext-secondary">
                            {rem.category}
                          </span>
                          <span className="text-xs text-dualtext-secondary flex items-center space-x-1">
                            <Clock className="w-3 h-3" />
                            <span>
                              {new Date(rem.scheduled_time).toLocaleTimeString([], {
                                hour: '2-digit',
                                minute: '2-digit',
                              })}
                            </span>
                          </span>
                        </div>
                        <div className="flex space-x-1">
                          {!rem.is_read && (
                            <button
                              onClick={() => markAsRead(rem.id)}
                              className="text-[11px] text-primary hover:underline px-1"
                            >
                              Read
                            </button>
                          )}
                          <button
                            onClick={() => dismissReminder(rem.id)}
                            className="text-[11px] text-dualtext-secondary hover:text-risk-red px-1"
                          >
                            Dismiss
                          </button>
                        </div>
                      </div>
                      <h4 className="text-xs font-semibold text-dualtext-primary mt-1">
                        {rem.title}
                      </h4>
                      <p className="text-xs text-dualtext-secondary mt-0.5 leading-relaxed">
                        {rem.message}
                      </p>
                    </div>
                  ))
                )}
              </div>
            </div>
          )}
        </div>

        {/* User profile pill */}
        <div className="flex items-center space-x-2 pl-2 border-l border-bordercolor">
          <button
            onClick={() => setActiveTab('privacy')}
            className="flex items-center space-x-2 p-1.5 rounded-xl hover:bg-dualbg transition-colors text-left"
          >
            <div className="w-8 h-8 rounded-full bg-primary/10 text-primary font-bold text-xs flex items-center justify-center border border-primary/20">
              {user?.full_name
                ? user.full_name.split(' ').map((n) => n[0]).join('')
                : 'U'}
            </div>
            <div className="hidden lg:block">
              <span className="text-xs font-semibold text-dualtext-primary block leading-tight">
                {user?.full_name || 'Student'}
              </span>
              <span className="text-[10px] text-dualtext-secondary block leading-tight">
                {profile?.major || 'CS & Bio'}
              </span>
            </div>
          </button>

          <button
            onClick={logout}
            className="p-2 rounded-xl text-dualtext-secondary hover:text-risk-red hover:bg-red-50 transition-colors"
            title="Log Out"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </header>
  );
};
