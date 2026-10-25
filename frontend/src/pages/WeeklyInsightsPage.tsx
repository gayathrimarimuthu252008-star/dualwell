import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import {
  BarChart3,
  Calendar,
  Activity,
  Moon,
  Droplet,
  Utensils,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  TrendingUp,
  PieChart as PieIcon,
  Clock
} from 'lucide-react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

export const WeeklyInsightsPage: React.FC = () => {
  const [insights, setInsights] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const fetchInsights = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/insights/weekly');
      setInsights(res.data);
    } catch (err) {
      console.error('Failed to load weekly insights:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  const trends = insights?.daily_trends || [];
  const riskDist = insights?.risk_distribution || { green_days: 4, yellow_days: 2, red_days: 1 };
  const taskData = insights?.completed_vs_missed_tasks || { completed: 3, pending: 1, total: 4 };

  return (
    <div className="space-y-6 pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-dualtext-primary">
            Weekly Insights & Predictive Analytics
          </h2>
          <p className="text-xs sm:text-sm text-dualtext-secondary">
            7-day multi-factorial analysis synthesized across coursework, athletic volume, and autonomic recovery.
          </p>
        </div>

        <div className="bg-white border border-bordercolor px-3.5 py-1.5 rounded-xl text-xs font-semibold text-dualtext-secondary flex items-center space-x-2 shadow-xs">
          <Calendar className="w-4 h-4 text-primary" />
          <span>{insights?.week_range}</span>
        </div>
      </div>

      {/* 4 Metric Consistency Tiles */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-white p-5 rounded-2xl border border-bordercolor shadow-xs">
          <div className="flex items-center space-x-2 text-dualtext-secondary text-xs mb-1">
            <Moon className="w-4 h-4 text-indigo-500" />
            <span className="font-semibold">Sleep Consistency</span>
          </div>
          <p className="text-2xl font-extrabold text-dualtext-primary mt-1">
            {insights?.sleep_consistency_score}%
          </p>
          <span className="text-[11px] text-risk-green font-semibold">Supportive circadian habit</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-bordercolor shadow-xs">
          <div className="flex items-center space-x-2 text-dualtext-secondary text-xs mb-1">
            <Droplet className="w-4 h-4 text-sky-500" />
            <span className="font-semibold">Hydration Consistency</span>
          </div>
          <p className="text-2xl font-extrabold text-sky-600 mt-1">
            {insights?.hydration_logging_consistency}%
          </p>
          <span className="text-[11px] text-dualtext-secondary">Days meeting 2L+ target</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-bordercolor shadow-xs">
          <div className="flex items-center space-x-2 text-dualtext-secondary text-xs mb-1">
            <Utensils className="w-4 h-4 text-amber-500" />
            <span className="font-semibold">Meal Logging Streak</span>
          </div>
          <p className="text-2xl font-extrabold text-dualtext-primary mt-1">
            {insights?.meal_logging_consistency}%
          </p>
          <span className="text-[11px] text-dualtext-secondary">Nutritional frequency</span>
        </div>

        <div className="bg-white p-5 rounded-2xl border border-bordercolor shadow-xs">
          <div className="flex items-center space-x-2 text-dualtext-secondary text-xs mb-1">
            <CheckCircle2 className="w-4 h-4 text-risk-green" />
            <span className="font-semibold">Deliverables Completed</span>
          </div>
          <p className="text-2xl font-extrabold text-dualtext-primary mt-1">
            {taskData.completed} / {taskData.total}
          </p>
          <span className="text-[11px] text-risk-green font-semibold">
            {Math.round((taskData.completed / Math.max(1, taskData.total)) * 100)}% on-time execution
          </span>
        </div>
      </div>

      {/* Workload vs Recovery 7-Day Chart */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 sm:p-6 shadow-xs space-y-4">
        <div>
          <h3 className="text-sm font-bold text-dualtext-primary">
            7-Day Dual Stress vs Recovery Trend
          </h3>
          <p className="text-xs text-dualtext-secondary">
            Notice how high academic spikes correlate with dips in physiological recovery readiness.
          </p>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={trends} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
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
              <Bar dataKey="academic_load" name="Academic Load" fill="#4F7DF3" radius={[4, 4, 0, 0]} />
              <Bar dataKey="athletic_load" name="Athletic Demand" fill="#239B68" radius={[4, 4, 0, 0]} />
              <Bar dataKey="recovery_score" name="Recovery Readiness" fill="#8B5CF6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Risk Distribution Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-mint/40 border border-emerald-200 p-5 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-risk-green uppercase">Optimal Days (Green)</span>
            <span className="w-2.5 h-2.5 rounded-full bg-risk-green" />
          </div>
          <p className="text-3xl font-extrabold text-risk-green">{riskDist.green_days} Days</p>
          <p className="text-xs text-dualtext-secondary mt-1">
            Readiness aligned well with workload. High focus and quality execution.
          </p>
        </div>

        <div className="bg-cream/50 border border-amber-200 p-5 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-risk-yellow uppercase">Elevated Load (Yellow)</span>
            <span className="w-2.5 h-2.5 rounded-full bg-risk-yellow" />
          </div>
          <p className="text-3xl font-extrabold text-risk-yellow">{riskDist.yellow_days} Days</p>
          <p className="text-xs text-dualtext-secondary mt-1">
            Tightened recovery capacity. Coursework concentration pushed into late afternoon.
          </p>
        </div>

        <div className="bg-red-50/70 border border-red-200 p-5 rounded-2xl shadow-xs">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold text-risk-red uppercase">Overload Triage (Red)</span>
            <span className="w-2.5 h-2.5 rounded-full bg-risk-red" />
          </div>
          <p className="text-3xl font-extrabold text-risk-red">{riskDist.red_days} Days</p>
          <p className="text-xs text-dualtext-secondary mt-1">
            Heavy cumulative deadlines coinciding with high-intensity athletic sessions.
          </p>
        </div>
      </div>

      {/* Key Actionable Recommendations for Next Week */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 sm:p-6 shadow-xs space-y-4">
        <div className="flex items-center space-x-2">
          <span className="p-2 rounded-xl bg-primary-soft text-primary">
            <Sparkles className="w-5 h-5" />
          </span>
          <div>
            <h3 className="text-sm font-bold text-dualtext-primary">
              AI-Generated Weekly Performance Recommendations
            </h3>
            <p className="text-xs text-dualtext-secondary">
              Personalized suggestions to enhance next week's athletic adaptation and GPA.
            </p>
          </div>
        </div>

        <div className="space-y-2.5 text-xs text-dualtext-secondary leading-relaxed">
          {insights?.key_recommendations?.map((rec: string, idx: number) => (
            <div key={idx} className="flex items-start space-x-3 p-3.5 rounded-xl bg-dualbg/60 border border-bordercolor">
              <span className="w-5 h-5 rounded-full bg-primary text-white text-[10px] font-bold flex items-center justify-center shrink-0 mt-0.5">
                {idx + 1}
              </span>
              <p className="text-dualtext-primary font-medium">{rec}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
