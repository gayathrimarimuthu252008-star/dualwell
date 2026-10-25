import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import {
  Moon,
  Clock,
  Sparkles,
  AlertCircle,
  Calendar,
  Activity,
  CheckCircle2,
  Bed,
  Sunset,
  Sunrise,
  ShieldCheck
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

export const SleepRecoveryPage: React.FC = () => {
  const [sleepRecords, setSleepRecords] = useState<any[]>([]);
  const [sleepPlan, setSleepPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchSleepData = async () => {
    try {
      setLoading(true);
      const [recRes, planRes] = await Promise.all([
        apiClient.get('/lifestyle/sleep'),
        apiClient.get('/lifestyle/sleep-plan')
      ]);
      setSleepRecords(recRes.data || []);
      setSleepPlan(planRes.data);
    } catch (err) {
      console.error('Failed to load sleep data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSleepData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  const latest = sleepRecords[0];
  const chartData = sleepRecords
    .slice(0, 7)
    .map((s) => ({
      date: new Date(s.sleep_end).toLocaleDateString([], { month: 'short', day: 'numeric' }),
      hours: s.duration_hours,
      deep: s.deep_sleep_hours || 1.6,
      rem: s.rem_sleep_hours || 1.8,
    }))
    .reverse();

  return (
    <div className="space-y-6 pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-dualtext-primary">
            Personalized Sleep Planner & Circadian Rhythm
          </h2>
          <p className="text-xs sm:text-sm text-dualtext-secondary">
            Protect neuro-cognitive memory consolidation and muscular recovery through disciplined sleep architecture.
          </p>
        </div>
      </div>

      {/* Non-Diagnostic Advisory */}
      <div className="bg-primary-soft/50 border border-primary/20 rounded-2xl p-4 flex items-center space-x-3 text-xs text-dualtext-secondary">
        <ShieldCheck className="w-5 h-5 text-primary shrink-0" />
        <span>
          <strong>Wellness Notice:</strong> DualWell provides non-medical behavioural scheduling recommendations to assist active students in protecting adequate rest. This system does not diagnose or treat medical sleep disorders.
        </span>
      </div>

      {/* Personalized Bedtime & Winddown Card */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 sm:p-6 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2">
            <span className="p-2 rounded-xl bg-indigo-50 text-indigo-600">
              <Moon className="w-5 h-5" />
            </span>
            <h3 className="text-base font-bold text-dualtext-primary">
              Personalized Sleep & Wind-Down Protocol
            </h3>
          </div>
          <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-mint text-risk-green border border-emerald-200 uppercase">
            Next-Day Load Aware
          </span>
        </div>

        {/* Schedule grid */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-5">
          <div className="bg-dualbg/60 p-4 rounded-xl border border-bordercolor">
            <div className="flex items-center space-x-2 text-dualtext-secondary mb-1">
              <Sunset className="w-4 h-4 text-amber-500" />
              <span className="text-xs font-semibold">Recommended Wind-Down</span>
            </div>
            <p className="text-2xl font-extrabold text-dualtext-primary">
              {sleepPlan?.recommended_winddown_time || '22:15'}
            </p>
            <span className="text-[11px] text-dualtext-secondary">Screen shutdown & dim lighting</span>
          </div>

          <div className="bg-dualbg/60 p-4 rounded-xl border border-bordercolor">
            <div className="flex items-center space-x-2 text-dualtext-secondary mb-1">
              <Bed className="w-4 h-4 text-indigo-500" />
              <span className="text-xs font-semibold">Target Bedtime</span>
            </div>
            <p className="text-2xl font-extrabold text-indigo-600">
              {sleepPlan?.target_bedtime || '23:00'}
            </p>
            <span className="text-[11px] text-dualtext-secondary">Full sleep latency window</span>
          </div>

          <div className="bg-dualbg/60 p-4 rounded-xl border border-bordercolor">
            <div className="flex items-center space-x-2 text-dualtext-secondary mb-1">
              <Sunrise className="w-4 h-4 text-sky-500" />
              <span className="text-xs font-semibold">Target Wake Time</span>
            </div>
            <p className="text-2xl font-extrabold text-dualtext-primary">
              {sleepPlan?.target_wake_time || '07:00'}
            </p>
            <span className="text-[11px] text-dualtext-secondary">
              Yields {sleepPlan?.sleep_target_hours || 8.0}h restorative sleep
            </span>
          </div>
        </div>

        {/* Advice banner */}
        <div className="bg-white p-4 rounded-xl border border-bordercolor space-y-2">
          <div className="flex items-center space-x-2 text-xs font-bold text-dualtext-primary">
            <Sparkles className="w-4 h-4 text-primary" />
            <span>Circadian Recommendation for Tonight:</span>
          </div>
          <p className="text-xs text-dualtext-secondary leading-relaxed">
            {sleepPlan?.advice || 'Prioritize an early wind-down to support tomorrow’s coursework.'}
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-2 border-t border-bordercolor text-xs text-dualtext-secondary">
            <div>
              <strong className="text-dualtext-primary">Tomorrow's Academic Demands:</strong> {sleepPlan?.academic_demand_tomorrow}
            </div>
            <div>
              <strong className="text-dualtext-primary">Tomorrow's Athletic Demands:</strong> {sleepPlan?.training_demand_tomorrow}
            </div>
          </div>
        </div>
      </div>

      {/* 7-Day Sleep Duration Visualization */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-sm font-bold text-dualtext-primary">
              7-Day Sleep History & Stages
            </h3>
            <p className="text-xs text-dualtext-secondary">
              Actual duration vs {sleepPlan?.sleep_target_hours || 8.0}h baseline target.
            </p>
          </div>
          <span className="text-xs text-dualtext-secondary">
            Avg: {latest?.duration_hours || 7.6} hours/night
          </span>
        </div>

        {chartData.length > 0 ? (
          <div className="h-60 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis dataKey="date" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} domain={[0, 10]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '12px',
                    border: '1px solid #E5E9F2',
                    fontSize: '12px',
                  }}
                />
                <Bar dataKey="hours" name="Total Hours" fill="#4F7DF3" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-dualtext-secondary">
            No sleep logs recorded yet.
          </div>
        )}
      </div>

      {/* Sleep Stages Breakdown for Latest Night */}
      {latest && (
        <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-bold text-dualtext-primary">
              Latest Sleep Architecture Breakdown
            </h3>
            <span className="text-[10px] bg-primary-soft text-primary font-bold px-2 py-0.5 rounded-full uppercase">
              {latest.data_source.replace('_', ' ')}
            </span>
          </div>

          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-center">
            <div className="p-3 bg-dualbg rounded-xl border border-bordercolor">
              <span className="text-[10px] uppercase font-bold text-dualtext-secondary">Deep Sleep</span>
              <p className="text-lg font-bold text-dualtext-primary mt-1">{latest.deep_sleep_hours || 1.7}h</p>
              <span className="text-[10px] text-gray-400">Physical repair</span>
            </div>
            <div className="p-3 bg-dualbg rounded-xl border border-bordercolor">
              <span className="text-[10px] uppercase font-bold text-dualtext-secondary">REM Sleep</span>
              <p className="text-lg font-bold text-primary mt-1">{latest.rem_sleep_hours || 1.8}h</p>
              <span className="text-[10px] text-gray-400">Memory & learning</span>
            </div>
            <div className="p-3 bg-dualbg rounded-xl border border-bordercolor">
              <span className="text-[10px] uppercase font-bold text-dualtext-secondary">Light Sleep</span>
              <p className="text-lg font-bold text-dualtext-primary mt-1">{latest.light_sleep_hours || 4.1}h</p>
              <span className="text-[10px] text-gray-400">Baseline rest</span>
            </div>
            <div className="p-3 bg-dualbg rounded-xl border border-bordercolor">
              <span className="text-[10px] uppercase font-bold text-dualtext-secondary">Efficiency</span>
              <p className="text-lg font-bold text-risk-green mt-1">{latest.efficiency_percentage || 89}%</p>
              <span className="text-[10px] text-gray-400">Restfulness</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
