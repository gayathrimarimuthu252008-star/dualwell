import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import {
  LifeBuoy,
  RefreshCw,
  CheckCircle2,
  Clock,
  AlertTriangle,
  ArrowRight,
  ShieldAlert,
  Flame,
  Droplet,
  Coffee,
  CheckSquare,
  Square
} from 'lucide-react';

export const PriorityRescueModePage: React.FC = () => {
  const [plan, setPlan] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [regenerating, setRegenerating] = useState(false);
  const [completedItems, setCompletedItems] = useState<Record<string, boolean>>({});

  const fetchRescuePlan = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/rescue/plan');
      setPlan(res.data);
    } catch (err) {
      console.error('Failed to load rescue plan:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRescuePlan();
  }, []);

  const handleRegenerate = async () => {
    try {
      setRegenerating(true);
      const res = await apiClient.post('/rescue/regenerate');
      setPlan(res.data);
      setCompletedItems({});
    } catch (err) {
      console.error('Regenerate failed:', err);
    } finally {
      setRegenerating(false);
    }
  };

  const toggleItem = (itemId: string) => {
    setCompletedItems((prev) => ({
      ...prev,
      [itemId]: !prev[itemId],
    }));
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-risk-red/30 border-t-risk-red rounded-full animate-spin" />
      </div>
    );
  }

  const nowItems = plan?.action_items?.filter((i: any) => i.urgency_tier === 'NOW') || [];
  const nextItems = plan?.action_items?.filter((i: any) => i.urgency_tier === 'NEXT') || [];
  const postponeItems = plan?.action_items?.filter((i: any) => i.urgency_tier === 'POSTPONE') || [];

  return (
    <div className="space-y-6 pb-12 max-w-4xl mx-auto">
      {/* Header Banner */}
      <div className="bg-red-50 border-2 border-risk-red/40 rounded-2xl p-5 sm:p-6 shadow-xs flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-3.5">
          <div className="p-3 rounded-2xl bg-risk-red text-white shadow-sm">
            <LifeBuoy className="w-7 h-7" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-risk-red text-white uppercase tracking-wider">
                Emergency Triage
              </span>
              <span className="text-xs font-semibold text-dualtext-secondary">
                Energy: {plan?.estimated_energy_level}
              </span>
            </div>
            <h2 className="text-lg sm:text-xl font-extrabold text-dualtext-primary mt-1">
              {plan?.summary_headline || 'Priority Rescue Mode'}
            </h2>
            <p className="text-xs text-dualtext-secondary">
              Understand what matters right now in under 60 seconds. Eliminate non-essential noise.
            </p>
          </div>
        </div>

        <button
          onClick={handleRegenerate}
          disabled={regenerating}
          className="flex items-center space-x-2 bg-white border border-risk-red/30 hover:border-risk-red text-risk-red text-xs sm:text-sm font-bold px-4 py-2.5 rounded-xl shadow-xs transition-colors self-start sm:self-auto shrink-0"
        >
          <RefreshCw className={`w-4 h-4 ${regenerating ? 'animate-spin' : ''}`} />
          <span>{regenerating ? 'Triage...' : 'Regenerate Plan'}</span>
        </button>
      </div>

      {/* 1. What to do NOW (Single Focused Sprint) */}
      <div className="bg-white rounded-2xl border-2 border-primary/50 p-5 sm:p-6 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="w-6 h-6 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center">
              1
            </span>
            <h3 className="text-base font-extrabold text-dualtext-primary tracking-tight">
              DO THIS RIGHT NOW (Immediate Single Sprint)
            </h3>
          </div>
          <span className="text-xs font-bold text-primary bg-primary-soft px-2.5 py-0.5 rounded-full">
            High Cognitive Priority
          </span>
        </div>

        {nowItems.map((item: any) => {
          const isDone = !!completedItems[item.id];
          return (
            <div
              key={item.id}
              onClick={() => toggleItem(item.id)}
              className={`p-4 rounded-xl border cursor-pointer transition-all ${
                isDone
                  ? 'bg-gray-50 border-bordercolor opacity-60'
                  : 'bg-primary-soft/20 border-primary/30 hover:bg-primary-soft/40'
              }`}
            >
              <div className="flex items-start space-x-3">
                <button className="mt-0.5 text-primary">
                  {isDone ? (
                    <CheckSquare className="w-5 h-5 text-risk-green" />
                  ) : (
                    <Square className="w-5 h-5" />
                  )}
                </button>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h4
                      className={`text-sm font-bold ${
                        isDone ? 'line-through text-dualtext-secondary' : 'text-dualtext-primary'
                      }`}
                    >
                      {item.title}
                    </h4>
                    <span className="text-xs font-semibold text-primary flex items-center space-x-1">
                      <Clock className="w-3.5 h-3.5" />
                      <span>{item.duration_minutes} Mins Focus Block</span>
                    </span>
                  </div>
                  <p className="text-xs text-dualtext-secondary mt-1 leading-relaxed">
                    {item.reason}
                  </p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* 2. What Must Be Done NEXT */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 sm:p-6 shadow-xs space-y-3">
        <div className="flex items-center space-x-2">
          <span className="w-6 h-6 rounded-full bg-dualtext-primary text-white text-xs font-bold flex items-center justify-center">
            2
          </span>
          <h3 className="text-base font-bold text-dualtext-primary">
            DO THIS NEXT (Secondary Checkpoint)
          </h3>
        </div>

        {nextItems.length === 0 ? (
          <p className="text-xs text-dualtext-secondary">No secondary deliverable today.</p>
        ) : (
          nextItems.map((item: any) => {
            const isDone = !!completedItems[item.id];
            return (
              <div
                key={item.id}
                onClick={() => toggleItem(item.id)}
                className={`p-4 rounded-xl border cursor-pointer transition-all ${
                  isDone
                    ? 'bg-gray-50 border-bordercolor opacity-60'
                    : 'bg-white border-bordercolor hover:border-dualtext-primary/40'
                }`}
              >
                <div className="flex items-start space-x-3">
                  <button className="mt-0.5 text-dualtext-secondary">
                    {isDone ? (
                      <CheckSquare className="w-5 h-5 text-risk-green" />
                    ) : (
                      <Square className="w-5 h-5" />
                    )}
                  </button>
                  <div className="flex-1">
                    <div className="flex items-center justify-between">
                      <h4
                        className={`text-sm font-bold ${
                          isDone ? 'line-through text-dualtext-secondary' : 'text-dualtext-primary'
                        }`}
                      >
                        {item.title}
                      </h4>
                      <span className="text-xs text-dualtext-secondary">
                        {item.duration_minutes} mins
                      </span>
                    </div>
                    <p className="text-xs text-dualtext-secondary mt-1">
                      {item.reason}
                    </p>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>

      {/* 3. Permissible to POSTPONE */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="w-6 h-6 rounded-full bg-emerald-600 text-white text-xs font-bold flex items-center justify-center">
              3
            </span>
            <h3 className="text-base font-bold text-dualtext-primary">
              SAFELY POSTPONE (Relieve Acute Cognitive Pressure)
            </h3>
          </div>
          <span className="text-[10px] bg-mint text-risk-green font-bold px-2 py-0.5 rounded-full uppercase">
            Stress Reducer
          </span>
        </div>

        {postponeItems.length === 0 ? (
          <p className="text-xs text-dualtext-secondary">
            No deferrable tasks; your schedule is already trimmed to essentials.
          </p>
        ) : (
          <div className="space-y-2">
            {postponeItems.map((item: any) => (
              <div
                key={item.id}
                className="p-3 bg-dualbg/60 rounded-xl border border-bordercolor flex items-center justify-between text-xs"
              >
                <span className="font-semibold text-dualtext-primary">{item.title}</span>
                <span className="text-dualtext-secondary italic">{item.reason}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* 4. Training Adjustment & Nutrition Intervention */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Training Adjustment */}
        <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs space-y-2">
          <div className="flex items-center space-x-2 text-dualtext-primary font-bold text-xs uppercase tracking-wider">
            <Flame className="w-4 h-4 text-risk-yellow" />
            <span>Athletic Training Adjustment</span>
          </div>
          <p className="text-xs text-dualtext-secondary leading-relaxed">
            {plan?.training_adjustment}
          </p>
        </div>

        {/* Hydration / Fuel */}
        <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs space-y-2">
          <div className="flex items-center space-x-2 text-dualtext-primary font-bold text-xs uppercase tracking-wider">
            <Droplet className="w-4 h-4 text-sky-500" />
            <span>Immediate Fuel & Fluid Directive</span>
          </div>
          <p className="text-xs text-dualtext-secondary leading-relaxed">
            {plan?.hydration_nutrition_alert}
          </p>
        </div>
      </div>
    </div>
  );
};
