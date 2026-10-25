import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import { NavTab } from '../components/layout/Sidebar';
import {
  Activity,
  BookOpen,
  Heart,
  Moon,
  Droplet,
  Plus,
  RefreshCw,
  Watch,
  LifeBuoy,
  ArrowRight,
  Sparkles,
  Clock,
  Calendar,
  AlertTriangle,
  CheckCircle2
} from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

interface DashboardPageProps {
  setActiveTab: (tab: NavTab) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ setActiveTab }) => {
  const { user } = useAuth();
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [riskData, setRiskData] = useState<any>(null);
  const [wearableStatus, setWearableStatus] = useState<any>(null);
  const [academicEvents, setAcademicEvents] = useState<any[]>([]);
  const [trainingSessions, setTrainingSessions] = useState<any[]>([]);
  const [hydrationData, setHydrationData] = useState<any>(null);
  const [sleepRecords, setSleepRecords] = useState<any[]>([]);
  const [weeklyTrends, setWeeklyTrends] = useState<any[]>([]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [riskRes, wearRes, acadRes, trainRes, hydRes, sleepRes, insightsRes] = await Promise.all([
        apiClient.get('/load-risk/current'),
        apiClient.get('/wearable/status'),
        apiClient.get('/academic/events'),
        apiClient.get('/training/sessions'),
        apiClient.get('/lifestyle/hydration'),
        apiClient.get('/lifestyle/sleep'),
        apiClient.get('/insights/weekly')
      ]);

      setRiskData(riskRes.data);
      setWearableStatus(wearRes.data);
      setAcademicEvents(acadRes.data || []);
      setTrainingSessions(trainRes.data || []);
      setHydrationData(hydRes.data);
      setSleepRecords(sleepRes.data || []);
      setWeeklyTrends(insightsRes.data.daily_trends || []);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const handleManualSync = async () => {
    try {
      setSyncing(true);
      await apiClient.post('/wearable/sync', { provider: 'demo' });
      await fetchDashboardData();
    } catch (err) {
      console.error('Sync failed:', err);
    } finally {
      setSyncing(false);
    }
  };

  const handleQuickAddWater = async () => {
    try {
      const res = await apiClient.post('/lifestyle/hydration/quick-add', { amount_ml: 250 });
      setHydrationData(res.data);
    } catch (err) {
      console.error('Failed to log water:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[70vh]">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-10 h-10 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
          <p className="text-xs font-semibold text-dualtext-secondary">
            Synchronizing student telemetry and academic load...
          </p>
        </div>
      </div>
    );
  }

  const latestSleep = sleepRecords[0];
  const combinedTimeline = [
    ...academicEvents.map((e) => ({
      id: `acad-${e.id}`,
      title: e.title,
      type: 'academic',
      start: new Date(e.start_time),
      end: new Date(e.end_time),
      priority: e.priority,
      tag: e.event_type,
    })),
    ...trainingSessions.map((t) => ({
      id: `train-${t.id}`,
      title: t.title,
      type: 'training',
      start: new Date(t.start_time),
      end: new Date(t.end_time),
      priority: t.intensity,
      tag: t.activity_type,
    })),
  ].sort((a, b) => a.start.getTime() - b.start.getTime());

  return (
    <div className="space-y-6 pb-12">
      {/* 1. Top Emergency Rescue Mode Banner if risk is elevated */}
      {riskData?.risk_level === 'RED' && (
        <div className="bg-red-50 border-2 border-risk-red/40 rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 shadow-sm animate-pulse">
          <div className="flex items-center space-x-3.5">
            <div className="p-2.5 rounded-xl bg-risk-red text-white">
              <LifeBuoy className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-sm sm:text-base font-bold text-risk-red">
                Critical Dual-Load Overload Detected
              </h3>
              <p className="text-xs text-dualtext-secondary mt-0.5">
                Academic deadline proximity and athletic training strain exceed recovery reserves.
              </p>
            </div>
          </div>
          <button
            onClick={() => setActiveTab('rescue')}
            className="w-full sm:w-auto px-4 py-2 bg-risk-red hover:bg-red-700 text-white text-xs font-bold rounded-xl shadow-sm transition-all flex items-center justify-center space-x-2 shrink-0"
          >
            <span>Activate Rescue Mode</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {/* 2. Top Greeting & Synchronization Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-dualtext-primary">
            Student Performance Dashboard
          </h2>
          <p className="text-xs sm:text-sm text-dualtext-secondary">
            Continuous balance tracking across coursework, workouts, and autonomic recovery.
          </p>
        </div>

        {/* Sync Status Button */}
        <div className="flex items-center space-x-2">
          <div className="bg-white border border-bordercolor px-3 py-1.5 rounded-xl text-xs flex items-center space-x-2 text-dualtext-secondary">
            <span className="w-2 h-2 rounded-full bg-risk-green" />
            <span>Connected: {wearableStatus?.active_provider === 'demo' ? 'Athlete Simulator' : wearableStatus?.active_provider}</span>
            {wearableStatus?.last_sync_time && (
              <span className="text-[10px] text-gray-400 pl-1 border-l border-bordercolor">
                {new Date(wearableStatus.last_sync_time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            )}
          </div>

          <button
            onClick={handleManualSync}
            disabled={syncing}
            className="flex items-center space-x-1.5 bg-white border border-bordercolor hover:border-primary text-dualtext-primary hover:text-primary px-3 py-1.5 rounded-xl text-xs font-semibold shadow-xs transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${syncing ? 'animate-spin text-primary' : ''}`} />
            <span>{syncing ? 'Syncing...' : 'Sync Wearable'}</span>
          </button>
        </div>
      </div>

      {/* 3. Primary KPI Load & Recovery Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Risk Score Card */}
        <div className="bg-white p-5 rounded-2xl border border-bordercolor shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-dualtext-secondary uppercase tracking-wider">
              Dual-Load Risk
            </span>
            <span
              className={`text-xs font-bold px-2.5 py-0.5 rounded-full ${
                riskData?.risk_level === 'GREEN'
                  ? 'bg-mint text-risk-green'
                  : riskData?.risk_level === 'YELLOW'
                  ? 'bg-cream text-risk-yellow'
                  : 'bg-red-100 text-risk-red'
              }`}
            >
              {riskData?.risk_level}
            </span>
          </div>
          <div className="my-3">
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-extrabold text-dualtext-primary">
                {riskData?.risk_score?.toFixed(0) || '54'}
              </span>
              <span className="text-xs text-dualtext-secondary">/ 100</span>
            </div>
            <div className="w-full bg-dualbg rounded-full h-2 mt-2 overflow-hidden">
              <div
                className={`h-2 rounded-full transition-all duration-500 ${
                  riskData?.risk_level === 'GREEN'
                    ? 'bg-risk-green'
                    : riskData?.risk_level === 'YELLOW'
                    ? 'bg-risk-yellow'
                    : 'bg-risk-red'
                }`}
                style={{ width: `${Math.min(100, riskData?.risk_score || 50)}%` }}
              />
            </div>
          </div>
          <p className="text-[11px] text-dualtext-secondary line-clamp-1">
            Confidence: {riskData?.confidence_score || 85}% • Rule-Based Estimator
          </p>
        </div>

        {/* Academic Load Card */}
        <div className="bg-white p-5 rounded-2xl border border-bordercolor shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-dualtext-secondary uppercase tracking-wider">
              Academic Load
            </span>
            <div className="p-1.5 rounded-lg bg-primary-soft text-primary">
              <BookOpen className="w-4 h-4" />
            </div>
          </div>
          <div className="my-3">
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-extrabold text-dualtext-primary">
                {riskData?.academic_component?.toFixed(0) || '62'}
              </span>
              <span className="text-xs text-dualtext-secondary">/ 100</span>
            </div>
            <div className="w-full bg-dualbg rounded-full h-2 mt-2 overflow-hidden">
              <div
                className="bg-primary h-2 rounded-full"
                style={{ width: `${Math.min(100, riskData?.academic_component || 60)}%` }}
              />
            </div>
          </div>
          <p className="text-[11px] text-dualtext-secondary">
            {academicEvents.filter((e) => !e.is_completed).length} pending coursework deliverables
          </p>
        </div>

        {/* Athletic Load Card */}
        <div className="bg-white p-5 rounded-2xl border border-bordercolor shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-dualtext-secondary uppercase tracking-wider">
              Athletic Strain
            </span>
            <div className="p-1.5 rounded-lg bg-mint text-risk-green">
              <Activity className="w-4 h-4" />
            </div>
          </div>
          <div className="my-3">
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-extrabold text-dualtext-primary">
                {riskData?.athletic_component?.toFixed(0) || '65'}
              </span>
              <span className="text-xs text-dualtext-secondary">/ 100</span>
            </div>
            <div className="w-full bg-dualbg rounded-full h-2 mt-2 overflow-hidden">
              <div
                className="bg-risk-green h-2 rounded-full"
                style={{ width: `${Math.min(100, riskData?.athletic_component || 65)}%` }}
              />
            </div>
          </div>
          <p className="text-[11px] text-dualtext-secondary">
            {trainingSessions.length} sessions logged this week
          </p>
        </div>

        {/* Recovery Readiness Card */}
        <div className="bg-white p-5 rounded-2xl border border-bordercolor shadow-xs flex flex-col justify-between">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold text-dualtext-secondary uppercase tracking-wider">
              Recovery Readiness
            </span>
            <div className="p-1.5 rounded-lg bg-indigo-50 text-indigo-600">
              <Heart className="w-4 h-4" />
            </div>
          </div>
          <div className="my-3">
            <div className="flex items-baseline space-x-2">
              <span className="text-3xl font-extrabold text-dualtext-primary">
                {riskData?.recovery_component?.toFixed(0) || '78'}
              </span>
              <span className="text-xs text-dualtext-secondary">/ 100</span>
            </div>
            <div className="w-full bg-dualbg rounded-full h-2 mt-2 overflow-hidden">
              <div
                className="bg-indigo-500 h-2 rounded-full"
                style={{ width: `${Math.min(100, riskData?.recovery_component || 75)}%` }}
              />
            </div>
          </div>
          <p className="text-[11px] text-dualtext-secondary">
            HRV baseline: {wearableStatus?.metrics_summary?.hrv || 62.5} ms
          </p>
        </div>
      </div>

      {/* 4. Action Banner */}
      <div className="bg-gradient-to-r from-primary/10 via-primary-soft to-transparent border border-primary/20 rounded-2xl p-4 sm:p-5 flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        <div className="flex items-start space-x-3">
          <div className="p-2 rounded-xl bg-primary text-white mt-0.5">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-dualtext-primary">
              Recommended Next Action: Focus on High-Urgency Problem Sets
            </h4>
            <p className="text-xs text-dualtext-secondary mt-0.5">
              {riskData?.recommended_actions?.[0] || 'Take a 15-minute mental break before starting your interval rowing practice.'}
            </p>
          </div>
        </div>
        <button
          onClick={() => setActiveTab('scheduler')}
          className="text-xs font-semibold text-primary hover:text-primary-hover flex items-center space-x-1 shrink-0"
        >
          <span>Review Schedule Adjustments</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* 5. Middle Grid: Timeline & Lifestyle Glances */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Today's Combined Timeline (2 cols on desktop) */}
        <div className="lg:col-span-2 bg-white rounded-2xl border border-bordercolor p-5 shadow-xs">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-primary" />
              <h3 className="text-sm font-bold text-dualtext-primary">
                Today's Integrated Schedule & Deadlines
              </h3>
            </div>
            <button
              onClick={() => setActiveTab('calendar')}
              className="text-xs text-primary font-semibold hover:underline"
            >
              Open Calendar
            </button>
          </div>

          <div className="space-y-3">
            {combinedTimeline.length === 0 ? (
              <div className="p-8 text-center text-xs text-dualtext-secondary">
                No events scheduled for today. Enjoy your recovery!
              </div>
            ) : (
              combinedTimeline.slice(0, 4).map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between p-3.5 rounded-xl border border-bordercolor hover:border-primary/40 transition-colors bg-white"
                >
                  <div className="flex items-center space-x-3">
                    <div
                      className={`w-2 h-10 rounded-full ${
                        item.type === 'academic' ? 'bg-primary' : 'bg-risk-green'
                      }`}
                    />
                    <div>
                      <h4 className="text-xs sm:text-sm font-semibold text-dualtext-primary">
                        {item.title}
                      </h4>
                      <div className="flex items-center space-x-2 text-[11px] text-dualtext-secondary mt-0.5">
                        <span className="flex items-center space-x-1">
                          <Clock className="w-3 h-3" />
                          <span>
                            {item.start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} –{' '}
                            {item.end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </span>
                        <span>•</span>
                        <span className="capitalize">{item.tag}</span>
                      </div>
                    </div>
                  </div>

                  <span
                    className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                      item.type === 'academic'
                        ? 'bg-primary-soft text-primary'
                        : 'bg-mint text-risk-green'
                    }`}
                  >
                    {item.type}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Right column: Hydration & Sleep glance cards */}
        <div className="space-y-6">
          {/* Hydration Widget */}
          <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Droplet className="w-4 h-4 text-sky-500" />
                <h3 className="text-sm font-bold text-dualtext-primary">Hydration Tracker</h3>
              </div>
              <button
                onClick={handleQuickAddWater}
                className="flex items-center space-x-1 bg-sky-50 hover:bg-sky-100 text-sky-600 px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors"
              >
                <Plus className="w-3.5 h-3.5" />
                <span>+250 mL</span>
              </button>
            </div>

            <div className="flex items-baseline justify-between mb-2">
              <span className="text-2xl font-extrabold text-dualtext-primary">
                {hydrationData?.total_consumed_ml || 0}
                <span className="text-xs font-normal text-dualtext-secondary ml-1">
                  / {hydrationData?.goal_ml || 2500} mL
                </span>
              </span>
              <span className="text-xs font-bold text-sky-600">
                {hydrationData?.percentage || 0}%
              </span>
            </div>

            <div className="w-full bg-dualbg rounded-full h-2.5 overflow-hidden">
              <div
                className="bg-sky-500 h-2.5 rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, hydrationData?.percentage || 0)}%` }}
              />
            </div>

            <p className="text-[11px] text-dualtext-secondary mt-3 leading-relaxed">
              {hydrationData?.smart_tip || 'Sip fluid consistently across study blocks.'}
            </p>
          </div>

          {/* Sleep Widget */}
          <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-2">
                <Moon className="w-4 h-4 text-indigo-500" />
                <h3 className="text-sm font-bold text-dualtext-primary">Sleep & Autonomic</h3>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-indigo-50 text-indigo-600">
                {latestSleep?.data_source === 'WEARABLE_LIVE' ? 'LIVE' : 'SIMULATED'}
              </span>
            </div>

            <div className="flex items-baseline space-x-2 mb-2">
              <span className="text-2xl font-extrabold text-dualtext-primary">
                {latestSleep?.duration_hours || 7.6}
              </span>
              <span className="text-xs text-dualtext-secondary">hours last night</span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-xs text-dualtext-secondary pt-2 border-t border-bordercolor">
              <div>
                <span className="block text-[10px] uppercase font-semibold text-gray-400">Resting HR</span>
                <span className="font-bold text-dualtext-primary">
                  {wearableStatus?.metrics_summary?.resting_hr || 53} bpm
                </span>
              </div>
              <div>
                <span className="block text-[10px] uppercase font-semibold text-gray-400">Daily Steps</span>
                <span className="font-bold text-dualtext-primary">
                  {wearableStatus?.metrics_summary?.steps?.toLocaleString() || '9,450'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 6. 7-Day Performance & Recovery Trend Chart */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
          <div>
            <h3 className="text-sm font-bold text-dualtext-primary">
              7-Day Academic Load vs Recovery Trend
            </h3>
            <p className="text-xs text-dualtext-secondary">
              Chronological daily breakdown of physiological readiness against dual stress factors.
            </p>
          </div>
          <button
            onClick={() => setActiveTab('insights')}
            className="text-xs text-primary font-semibold hover:underline"
          >
            View Full Analytics
          </button>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={weeklyTrends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
              <XAxis dataKey="day" stroke="#94A3B8" fontSize={11} tickLine={false} />
              <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} domain={[0, 100]} />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#FFFFFF',
                  borderRadius: '12px',
                  border: '1px solid #E5E9F2',
                  fontSize: '12px',
                }}
              />
              <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
              <Line
                type="monotone"
                dataKey="academic_load"
                name="Academic Load"
                stroke="#4F7DF3"
                strokeWidth={2.5}
                dot={{ r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="athletic_load"
                name="Athletic Strain"
                stroke="#239B68"
                strokeWidth={2.5}
                dot={{ r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="recovery_score"
                name="Recovery Readiness"
                stroke="#8B5CF6"
                strokeWidth={2.5}
                dot={{ r: 3 }}
              />
              <Line
                type="monotone"
                dataKey="dual_risk"
                name="Overload Risk"
                stroke="#E05252"
                strokeDasharray="4 4"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
