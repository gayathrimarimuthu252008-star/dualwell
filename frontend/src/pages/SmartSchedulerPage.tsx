import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import {
  Sparkles,
  ArrowRight,
  Check,
  X,
  Clock,
  ShieldAlert,
  Moon,
  Coffee,
  Calendar,
  RefreshCw,
  AlertCircle,
  ThumbsUp
} from 'lucide-react';

export const SmartSchedulerPage: React.FC = () => {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [optimizing, setOptimizing] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/scheduler/recommendations');
      setRecommendations(res.data || []);
    } catch (err) {
      console.error('Failed to fetch recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const handleApply = async (id: number) => {
    try {
      const res = await apiClient.post(`/scheduler/apply/${id}`);
      setSuccessMessage(res.data.message);
      setTimeout(() => setSuccessMessage(null), 4000);
      await fetchRecommendations();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to apply schedule adjustment.');
    }
  };

  const handleReject = async (id: number) => {
    try {
      await apiClient.post(`/scheduler/reject/${id}`);
      await fetchRecommendations();
    } catch (err) {
      console.error('Failed to dismiss recommendation:', err);
    }
  };

  const handleForceGenerate = async () => {
    try {
      setOptimizing(true);
      const res = await apiClient.post('/scheduler/generate');
      setRecommendations(res.data || []);
    } catch (err) {
      console.error('Optimization error:', err);
    } finally {
      setOptimizing(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-dualtext-primary">
            Smart Dynamic Scheduler
          </h2>
          <p className="text-xs sm:text-sm text-dualtext-secondary">
            AI-driven timetable adjustments to resolve time clashes, protect sleep windows, and prevent mental exhaustion.
          </p>
        </div>

        <button
          onClick={handleForceGenerate}
          disabled={optimizing}
          className="flex items-center space-x-2 bg-primary hover:bg-primary-hover text-white text-xs sm:text-sm font-semibold px-4 py-2 rounded-xl shadow-xs transition-colors self-start sm:self-auto"
        >
          <Sparkles className={`w-4 h-4 ${optimizing ? 'animate-spin' : ''}`} />
          <span>{optimizing ? 'Analyzing Conflicts...' : 'Re-Analyze Schedule'}</span>
        </button>
      </div>

      {successMessage && (
        <div className="bg-mint border border-emerald-300 text-risk-green text-xs sm:text-sm p-4 rounded-2xl flex items-center space-x-2 shadow-xs">
          <Check className="w-5 h-5 shrink-0" />
          <span className="font-semibold">{successMessage}</span>
        </div>
      )}

      {/* Safety Guarantee Banner */}
      <div className="bg-white rounded-2xl border border-bordercolor p-4 sm:p-5 shadow-xs flex items-start space-x-3.5">
        <div className="p-2 rounded-xl bg-primary-soft text-primary shrink-0">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div className="text-xs text-dualtext-secondary leading-relaxed">
          <strong className="text-dualtext-primary block text-sm mb-0.5">
            Non-Destructive Scheduling Guarantee
          </strong>
          Fixed obligations (final exams, required lectures) are strictly preserved and never moved. The scheduler proposes shifts only for flexible study sessions or adjustable workouts, inserting cognitive buffers and protecting your 8-hour sleep window. No changes are applied without your explicit confirmation.
        </div>
      </div>

      {/* Recommendations Feed */}
      <div>
        <h3 className="text-sm font-bold text-dualtext-primary mb-3">
          Proposed Schedule Adjustments ({recommendations.length} Pending)
        </h3>

        {loading ? (
          <div className="flex justify-center p-12">
            <div className="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
          </div>
        ) : recommendations.length === 0 ? (
          <div className="bg-white rounded-2xl border border-bordercolor p-12 text-center shadow-xs">
            <ThumbsUp className="w-12 h-12 text-risk-green mx-auto mb-3 opacity-60" />
            <h3 className="text-sm font-bold text-dualtext-primary">
              Your Timetable is Fully Balanced!
            </h3>
            <p className="text-xs text-dualtext-secondary mt-1 max-w-md mx-auto">
              No overlapping commitments, bedtime encroachments, or dangerously extended study blocks were detected.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {recommendations.map((rec) => {
              const origStart = rec.original_start_time ? new Date(rec.original_start_time) : null;
              const origEnd = rec.original_end_time ? new Date(rec.original_end_time) : null;
              const propStart = new Date(rec.proposed_start_time);
              const propEnd = new Date(rec.proposed_end_time);

              const isSleepProtection = rec.action_type === 'EARLY_WINDDOWN';
              const isRestBuffer = rec.action_type === 'INSERT_REST';

              return (
                <div
                  key={rec.id}
                  className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs hover:border-primary/40 transition-all space-y-4"
                >
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-bordercolor pb-3">
                    <div className="flex items-center space-x-2">
                      <span
                        className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full uppercase ${
                          isSleepProtection
                            ? 'bg-indigo-50 text-indigo-600 border border-indigo-200'
                            : isRestBuffer
                            ? 'bg-mint text-risk-green border border-emerald-200'
                            : 'bg-primary-soft text-primary border border-primary/20'
                        }`}
                      >
                        {rec.action_type.replace('_', ' ')}
                      </span>
                      <h4 className="text-sm font-bold text-dualtext-primary">
                        {rec.event_title}
                      </h4>
                    </div>

                    <span className="text-[11px] text-dualtext-secondary capitalize">
                      Category: {rec.event_category}
                    </span>
                  </div>

                  {/* Before vs After Schedule comparison */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-dualbg/60 p-3.5 rounded-xl border border-bordercolor">
                    {/* Original */}
                    <div className="space-y-1 text-xs">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-dualtext-secondary">
                        Original Time Slot
                      </span>
                      <div className="font-semibold text-dualtext-secondary flex items-center space-x-1.5">
                        <Clock className="w-3.5 h-3.5" />
                        <span>
                          {origStart
                            ? `${origStart.toLocaleDateString([], { month: 'short', day: 'numeric' })} • ${origStart.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`
                            : 'Unscheduled buffer'}
                          {origEnd ? ` – ${origEnd.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}` : ''}
                        </span>
                      </div>
                    </div>

                    {/* Proposed */}
                    <div className="space-y-1 text-xs border-t md:border-t-0 md:border-l border-bordercolor pt-2 md:pt-0 md:pl-3">
                      <span className="text-[10px] font-bold uppercase tracking-wider text-primary">
                        Proposed Optimized Time
                      </span>
                      <div className="font-bold text-dualtext-primary flex items-center space-x-1.5">
                        <Clock className="w-3.5 h-3.5 text-primary" />
                        <span>
                          {propStart.toLocaleDateString([], { month: 'short', day: 'numeric' })} •{' '}
                          {propStart.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })} –{' '}
                          {propEnd.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* Rationale */}
                  <div className="text-xs text-dualtext-secondary bg-white p-3 rounded-xl border border-bordercolor">
                    <strong className="text-dualtext-primary block mb-0.5">
                      Scheduler Rationale:
                    </strong>
                    <p className="leading-relaxed">{rec.rationale}</p>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center justify-end space-x-2 pt-1">
                    <button
                      onClick={() => handleReject(rec.id)}
                      className="px-4 py-2 border border-bordercolor text-dualtext-secondary hover:text-risk-red text-xs font-semibold rounded-xl transition-colors"
                    >
                      Dismiss
                    </button>
                    <button
                      onClick={() => handleApply(rec.id)}
                      className="flex items-center space-x-1.5 px-4 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-xl shadow-xs transition-colors"
                    >
                      <Check className="w-4 h-4" />
                      <span>Confirm & Apply Adjustment</span>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
