import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import {
  ShieldCheck,
  Download,
  Trash2,
  Save,
  CheckCircle,
  AlertTriangle,
  Lock,
  Moon,
  Bell,
  Watch,
  User
} from 'lucide-react';

export const PrivacySettingsPage: React.FC = () => {
  const { user, profile, refreshProfile, logout } = useAuth();
  const [privacySettings, setPrivacySettings] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Profile edit state
  const [major, setMajor] = useState('');
  const [sport, setSport] = useState('');
  const [sleepTarget, setSleepTarget] = useState(8.0);
  const [bedtime, setBedtime] = useState('23:00');
  const [wakeTime, setWakeTime] = useState('07:00');
  const [hydrationGoal, setHydrationGoal] = useState(2500);
  const [academicGoals, setAcademicGoals] = useState('');

  // Privacy toggles state
  const [consentWearable, setConsentWearable] = useState(true);
  const [allowNotifications, setAllowNotifications] = useState(true);
  const [quietHours, setQuietHours] = useState(true);
  const [quietStart, setQuietStart] = useState('22:30');
  const [quietEnd, setQuietEnd] = useState('06:30');

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        const res = await apiClient.get('/privacy/settings');
        setPrivacySettings(res.data);
        setConsentWearable(res.data.consent_wearable_sync);
        setAllowNotifications(res.data.allow_overload_notifications);
        setQuietHours(res.data.quiet_hours_enabled);
        setQuietStart(res.data.quiet_hours_start);
        setQuietEnd(res.data.quiet_hours_end);

        if (profile) {
          setMajor(profile.major || '');
          setSport(profile.primary_sport || '');
          setSleepTarget(profile.usual_sleep_target_hours || 8.0);
          setBedtime(profile.usual_bedtime || '23:00');
          setWakeTime(profile.usual_wake_time || '07:00');
          setHydrationGoal(profile.daily_hydration_goal_ml || 2500);
          setAcademicGoals(profile.academic_goals || '');
        }
      } catch (err) {
        console.error('Failed to load privacy settings:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchSettings();
  }, [profile]);

  const handleSaveAll = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      // Save profile
      await apiClient.put('/auth/profile', {
        major,
        primary_sport: sport,
        usual_sleep_target_hours: Number(sleepTarget),
        usual_bedtime: bedtime,
        usual_wake_time: wakeTime,
        daily_hydration_goal_ml: Number(hydrationGoal),
        academic_goals: academicGoals,
      });

      // Save privacy preferences
      await apiClient.put('/privacy/settings', {
        consent_wearable_sync: consentWearable,
        allow_overload_notifications: allowNotifications,
        quiet_hours_enabled: quietHours,
        quiet_hours_start: quietStart,
        quiet_hours_end: quietEnd,
      });

      await refreshProfile();
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 4000);
    } catch (err) {
      console.error('Failed to save settings:', err);
    }
  };

  const handleExportData = async () => {
    try {
      const res = await apiClient.get('/privacy/export-data', { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `dualwell_student_data_export_${user?.id}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  const handleDeleteAccount = async () => {
    const confirmation = prompt(
      'WARNING: This will permanently delete your account, study history, and telemetry records. Type "DELETE" to confirm:'
    );
    if (confirmation !== 'DELETE') return;

    const password = prompt('Re-enter your account password to confirm permanent deletion:');
    if (!password) {
      alert('Account deletion cancelled: a password is required.');
      return;
    }

    try {
      await apiClient.delete('/privacy/delete-account', { data: { password } });
      alert('Your account and all associated data have been permanently erased.');
      localStorage.removeItem('dualwell_token');
      localStorage.removeItem('dualwell_refresh_token');
      logout();
    } catch (err: any) {
      const detail = err.response?.data?.detail;
      alert(detail || 'Account deletion failed. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6 pb-12 max-w-4xl">
      {/* Header */}
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-dualtext-primary">
          Privacy Controls, Data Rights & Student Profile
        </h2>
        <p className="text-xs sm:text-sm text-dualtext-secondary">
          Manage your biometric consent, telemetry retention, quiet hours, and personal academic targets.
        </p>
      </div>

      {saveSuccess && (
        <div className="bg-mint border border-emerald-300 text-risk-green text-xs sm:text-sm p-4 rounded-2xl flex items-center space-x-2 shadow-xs">
          <CheckCircle className="w-5 h-5 shrink-0" />
          <span className="font-semibold">Student preferences and privacy toggles saved successfully!</span>
        </div>
      )}

      <form onSubmit={handleSaveAll} className="space-y-6">
        {/* 1. Student Profile Settings */}
        <div className="bg-white rounded-2xl border border-bordercolor p-5 sm:p-6 shadow-xs space-y-4">
          <div className="flex items-center space-x-2 border-b border-bordercolor pb-3">
            <User className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-bold text-dualtext-primary">
              Student-Athlete Profile & Baselines
            </h3>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-medium text-dualtext-primary mb-1">
                Academic Major / Discipline
              </label>
              <input
                type="text"
                value={major}
                onChange={(e) => setMajor(e.target.value)}
                className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-dualtext-primary mb-1">
                Primary Sport / Athletic Focus
              </label>
              <input
                type="text"
                value={sport}
                onChange={(e) => setSport(e.target.value)}
                className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <label className="block text-xs font-medium text-dualtext-primary mb-1">
                Sleep Target (Hours)
              </label>
              <input
                type="number"
                step="0.5"
                min="6"
                max="10"
                value={sleepTarget}
                onChange={(e) => setSleepTarget(Number(e.target.value))}
                className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-dualtext-primary mb-1">
                Usual Bedtime
              </label>
              <input
                type="time"
                value={bedtime}
                onChange={(e) => setBedtime(e.target.value)}
                className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-dualtext-primary mb-1">
                Usual Wake Time
              </label>
              <input
                type="time"
                value={wakeTime}
                onChange={(e) => setWakeTime(e.target.value)}
                className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-medium text-dualtext-primary mb-1">
              Daily Hydration Target (mL)
            </label>
            <input
              type="number"
              step="100"
              min="1500"
              max="5000"
              value={hydrationGoal}
              onChange={(e) => setHydrationGoal(Number(e.target.value))}
              className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary max-w-xs"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-dualtext-primary mb-1">
              Academic & Athletic Peak Goals
            </label>
            <textarea
              rows={2}
              value={academicGoals}
              onChange={(e) => setAcademicGoals(e.target.value)}
              className="w-full px-3 py-2 border border-bordercolor rounded-xl text-xs sm:text-sm focus:outline-none focus:ring-2 focus:ring-primary"
            />
          </div>
        </div>

        {/* 2. Privacy & Data Consent Settings */}
        <div className="bg-white rounded-2xl border border-bordercolor p-5 sm:p-6 shadow-xs space-y-4">
          <div className="flex items-center space-x-2 border-b border-bordercolor pb-3">
            <ShieldCheck className="w-4 h-4 text-primary" />
            <h3 className="text-sm font-bold text-dualtext-primary">
              Biometric Data Consent & In-App Alarms
            </h3>
          </div>

          <div className="space-y-4">
            <div className="flex items-start justify-between">
              <div>
                <span className="text-xs font-bold text-dualtext-primary block">
                  Consent for Wearable Telemetry Synchronization
                </span>
                <span className="text-xs text-dualtext-secondary leading-relaxed">
                  Allow DualWell to poll heart rate, HRV, sleep metrics, and activity from your connected watch provider.
                </span>
              </div>
              <input
                type="checkbox"
                checked={consentWearable}
                onChange={(e) => setConsentWearable(e.target.checked)}
                className="mt-1 rounded text-primary focus:ring-primary w-4 h-4"
              />
            </div>

            <div className="flex items-start justify-between pt-3 border-t border-bordercolor">
              <div>
                <span className="text-xs font-bold text-dualtext-primary block">
                  In-App Overload & Hydration Nudges
                </span>
                <span className="text-xs text-dualtext-secondary leading-relaxed">
                  Generate in-app reminder cards for urgent deadlines, water refills, and training cool-down alerts.
                </span>
              </div>
              <input
                type="checkbox"
                checked={allowNotifications}
                onChange={(e) => setAllowNotifications(e.target.checked)}
                className="mt-1 rounded text-primary focus:ring-primary w-4 h-4"
              />
            </div>

            <div className="pt-3 border-t border-bordercolor space-y-3">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-bold text-dualtext-primary block">
                    Enable Quiet Hours (No Audio / Popups)
                  </span>
                  <span className="text-xs text-dualtext-secondary">
                    Suppress in-app reminder notifications during your restorative sleep window.
                  </span>
                </div>
                <input
                  type="checkbox"
                  checked={quietHours}
                  onChange={(e) => setQuietHours(e.target.checked)}
                  className="mt-1 rounded text-primary focus:ring-primary w-4 h-4"
                />
              </div>

              {quietHours && (
                <div className="flex items-center space-x-3 bg-dualbg/60 p-3 rounded-xl border border-bordercolor">
                  <div>
                    <label className="block text-[10px] uppercase font-bold text-dualtext-secondary mb-1">
                      Quiet Hours Start
                    </label>
                    <input
                      type="time"
                      value={quietStart}
                      onChange={(e) => setQuietStart(e.target.value)}
                      className="px-2.5 py-1 border border-bordercolor rounded-lg text-xs bg-white"
                    />
                  </div>
                  <span className="text-dualtext-secondary pt-3">to</span>
                  <div>
                    <label className="block text-[10px] uppercase font-bold text-dualtext-secondary mb-1">
                      Quiet Hours End
                    </label>
                    <input
                      type="time"
                      value={quietEnd}
                      onChange={(e) => setQuietEnd(e.target.value)}
                      className="px-2.5 py-1 border border-bordercolor rounded-lg text-xs bg-white"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <button
          type="submit"
          className="flex items-center space-x-2 bg-primary hover:bg-primary-hover text-white text-xs sm:text-sm font-semibold px-5 py-2.5 rounded-xl shadow-xs transition-colors"
        >
          <Save className="w-4 h-4" />
          <span>Save Profile & Privacy Preferences</span>
        </button>
      </form>

      {/* 3. Data Governance & Export/Delete Section */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 sm:p-6 shadow-xs space-y-4">
        <div className="flex items-center space-x-2 border-b border-bordercolor pb-3">
          <Lock className="w-4 h-4 text-primary" />
          <h3 className="text-sm font-bold text-dualtext-primary">
            Student Data Portability & Deletion Rights
          </h3>
        </div>

        <div className="space-y-4 text-xs text-dualtext-secondary">
          <p className="leading-relaxed">
            In accordance with student data privacy best practices, you retain full sovereignty over your physical activity, sleep records, coursework schedule, and nutritional logs. All data remains stored in your isolated database partitions.
          </p>

          <div className="flex flex-col sm:flex-row gap-3 pt-2">
            <button
              type="button"
              onClick={handleExportData}
              className="flex items-center justify-center space-x-2 bg-white border border-bordercolor hover:border-primary text-dualtext-primary hover:text-primary px-4 py-2.5 rounded-xl font-semibold shadow-xs transition-colors"
            >
              <Download className="w-4 h-4" />
              <span>Export Complete Student Data (.JSON)</span>
            </button>

            <button
              type="button"
              onClick={handleDeleteAccount}
              className="flex items-center justify-center space-x-2 bg-red-50 hover:bg-red-100 text-risk-red border border-red-200 px-4 py-2.5 rounded-xl font-semibold transition-colors"
            >
              <Trash2 className="w-4 h-4" />
              <span>Permanently Delete Student Account & Records</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
