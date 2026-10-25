import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import {
  HeartPulse,
  AlertOctagon,
  Sparkles,
  CheckCircle,
  Activity,
  Flame,
  Wind,
  ShieldAlert,
  ArrowRight
} from 'lucide-react';

export const RecoveryGuidePage: React.FC = () => {
  const [guideData, setGuideData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [showCheckInModal, setShowCheckInModal] = useState(false);

  // Checkin state
  const [soreness, setSoreness] = useState(3);
  const [mentalFatigue, setMentalFatigue] = useState(3);
  const [readiness, setReadiness] = useState(8);
  const [hasPain, setHasPain] = useState(false);
  const [painDetails, setPainDetails] = useState('');
  const [checkinSuccess, setCheckinSuccess] = useState(false);

  const fetchGuideContent = async () => {
    try {
      setLoading(true);
      const res = await apiClient.get('/recovery-guide/content');
      setGuideData(res.data);
    } catch (err) {
      console.error('Failed to load recovery content:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGuideContent();
  }, []);

  const handleSubmitCheckin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await apiClient.post('/lifestyle/recovery-checkin', {
        muscle_soreness: soreness,
        mental_fatigue: mentalFatigue,
        sleep_readiness: readiness,
        has_pain_or_strain: hasPain,
        pain_details: hasPain ? painDetails : null,
      });

      setShowCheckInModal(false);
      setCheckinSuccess(true);
      setTimeout(() => setCheckinSuccess(false), 4000);
      await fetchGuideContent();
    } catch (err) {
      console.error('Checkin failed:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  const studyMode = guideData?.energy_aware_study_suggestion;

  return (
    <div className="space-y-6 pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-dualtext-primary">
            Recovery & Active Rehabilitation Guide
          </h2>
          <p className="text-xs sm:text-sm text-dualtext-secondary">
            Restoration protocols, gentle mobility routines, and energy-aware academic planning.
          </p>
        </div>

        <button
          onClick={() => setShowCheckInModal(true)}
          className="flex items-center space-x-1.5 bg-primary hover:bg-primary-hover text-white text-xs sm:text-sm font-semibold px-4 py-2 rounded-xl shadow-xs transition-colors self-start sm:self-auto"
        >
          <Activity className="w-4 h-4" />
          <span>Fatigue & Soreness Self-Check</span>
        </button>
      </div>

      {checkinSuccess && (
        <div className="bg-mint border border-emerald-300 text-risk-green text-xs sm:text-sm p-4 rounded-2xl flex items-center space-x-2 shadow-xs">
          <CheckCircle className="w-5 h-5 shrink-0" />
          <span className="font-semibold">Fatigue self-check successfully recorded! Dual-load engine updated.</span>
        </div>
      )}

      {/* Mandatory Medical Safety Disclaimer Banner */}
      <div className="bg-red-50 border-2 border-risk-red/30 rounded-2xl p-4 sm:p-5 flex items-start space-x-3.5 shadow-xs">
        <div className="p-2 rounded-xl bg-risk-red text-white shrink-0 mt-0.5">
          <AlertOctagon className="w-5 h-5" />
        </div>
        <div className="text-xs text-dualtext-secondary leading-relaxed">
          <strong className="text-risk-red block text-sm font-bold mb-1">
            CRITICAL MEDICAL DISCLAIMER
          </strong>
          {guideData?.medical_disclaimer ||
            'DualWell is an educational student-wellness aid and not a medical device. If you experience sharp, persistent, worsening, or radiating musculoskeletal pain, cease physical training immediately and seek professional evaluation from campus health services or a licensed sports medicine physician.'}
        </div>
      </div>

      {/* Energy-Aware Study Recommendation Card (FR12) */}
      {studyMode && (
        <div className="bg-white rounded-2xl border border-bordercolor p-5 sm:p-6 shadow-xs">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center space-x-2">
              <span className="p-2 rounded-xl bg-primary-soft text-primary">
                <Sparkles className="w-5 h-5" />
              </span>
              <div>
                <h3 className="text-base font-bold text-dualtext-primary">
                  Energy-Aware Study Session Mode
                </h3>
                <p className="text-xs text-dualtext-secondary">
                  Calibrated to your current autonomic readiness score.
                </p>
              </div>
            </div>
            <span className="text-xs font-bold px-3 py-1 rounded-full bg-primary-soft text-primary">
              {studyMode.mode}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3 my-4 bg-dualbg/60 p-4 rounded-xl border border-bordercolor">
            <div>
              <span className="text-[10px] uppercase font-bold text-dualtext-secondary">Sprint Duration</span>
              <p className="text-lg font-bold text-dualtext-primary">{studyMode.recommended_duration_min} mins</p>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-dualtext-secondary">Mandatory Rest Break</span>
              <p className="text-lg font-bold text-risk-green">{studyMode.break_duration_min} mins</p>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-dualtext-secondary">Target Cognitive Focus</span>
              <p className="text-xs font-semibold text-dualtext-primary line-clamp-2">{studyMode.focus_type}</p>
            </div>
          </div>

          <p className="text-xs text-dualtext-secondary leading-relaxed">
            <strong>Physiological Rationale:</strong> {studyMode.rationale}
          </p>
        </div>
      )}

      {/* Gentle Mobility Routines */}
      <div>
        <h3 className="text-sm font-bold text-dualtext-primary mb-3">
          Gentle Student-Athlete Mobility Sequences
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {guideData?.gentle_mobility_routines?.map((mob: any) => (
            <div
              key={mob.id}
              className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-[10px] font-bold px-2.5 py-0.5 rounded-full bg-mint text-risk-green border border-emerald-200">
                    {mob.duration_minutes} Minutes
                  </span>
                  <Wind className="w-4 h-4 text-dualtext-secondary" />
                </div>
                <h4 className="font-bold text-sm text-dualtext-primary mb-1">
                  {mob.title}
                </h4>
                <p className="text-xs text-primary font-semibold mb-3">
                  Target: {mob.target_area}
                </p>

                <div className="space-y-2 border-t border-bordercolor pt-3 text-xs text-dualtext-secondary">
                  {mob.steps?.map((step: string, idx: number) => (
                    <div key={idx} className="flex items-start space-x-2">
                      <span className="text-primary font-bold">{idx + 1}.</span>
                      <span className="leading-relaxed">{step}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Warm-Up and Cool-Down Protocols */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Warm-up */}
        <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs">
          <div className="flex items-center space-x-2 mb-3">
            <Flame className="w-5 h-5 text-amber-500" />
            <h3 className="text-sm font-bold text-dualtext-primary">
              Pre-Workout Dynamic Warm-Up Protocol
            </h3>
          </div>
          <ul className="space-y-2 text-xs text-dualtext-secondary">
            {guideData?.warmup_guidelines?.map((item: string, idx: number) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-amber-500 font-bold">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Cool-down */}
        <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs">
          <div className="flex items-center space-x-2 mb-3">
            <Wind className="w-5 h-5 text-sky-500" />
            <h3 className="text-sm font-bold text-dualtext-primary">
              Post-Workout Cool-Down & Downregulation
            </h3>
          </div>
          <ul className="space-y-2 text-xs text-dualtext-secondary">
            {guideData?.cooldown_guidelines?.map((item: string, idx: number) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="text-sky-500 font-bold">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Fatigue Self-Check Modal */}
      {showCheckInModal && (
        <div className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 border border-bordercolor shadow-xl">
            <div className="flex items-center justify-between mb-4 border-b border-bordercolor pb-3">
              <h3 className="text-base font-bold text-dualtext-primary">
                Daily Fatigue & Recovery Check-In
              </h3>
              <button
                onClick={() => setShowCheckInModal(false)}
                className="text-dualtext-secondary hover:text-dualtext-primary text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <form onSubmit={handleSubmitCheckin} className="space-y-4">
              <div>
                <div className="flex justify-between text-xs font-medium text-dualtext-primary mb-1">
                  <span>Muscle Soreness (1 = Fresh, 10 = Severe)</span>
                  <span className="font-bold text-primary">{soreness} / 10</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={soreness}
                  onChange={(e) => setSoreness(Number(e.target.value))}
                  className="w-full accent-primary"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-dualtext-primary mb-1">
                  <span>Mental / Cognitive Fatigue (1 = Clear, 10 = Exhausted)</span>
                  <span className="font-bold text-primary">{mentalFatigue} / 10</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={mentalFatigue}
                  onChange={(e) => setMentalFatigue(Number(e.target.value))}
                  className="w-full accent-primary"
                />
              </div>

              <div>
                <div className="flex justify-between text-xs font-medium text-dualtext-primary mb-1">
                  <span>Physical Readiness (1 = Depleted, 10 = Peak)</span>
                  <span className="font-bold text-risk-green">{readiness} / 10</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="10"
                  value={readiness}
                  onChange={(e) => setReadiness(Number(e.target.value))}
                  className="w-full accent-risk-green"
                />
              </div>

              <div className="pt-2 border-t border-bordercolor">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="painFlag"
                    checked={hasPain}
                    onChange={(e) => setHasPain(e.target.checked)}
                    className="rounded text-risk-red focus:ring-risk-red"
                  />
                  <label htmlFor="painFlag" className="text-xs font-bold text-risk-red">
                    I am experiencing joint pain, sharp strain, or injury symptoms
                  </label>
                </div>

                {hasPain && (
                  <div className="mt-2 space-y-1">
                    <textarea
                      rows={2}
                      value={painDetails}
                      onChange={(e) => setPainDetails(e.target.value)}
                      placeholder="Describe location (e.g. knee patellar tendon) and symptom severity..."
                      className="w-full px-3 py-2 border border-red-300 rounded-xl text-xs focus:ring-2 focus:ring-risk-red"
                    />
                    <p className="text-[11px] text-risk-red italic">
                      Notice: If symptoms are sharp or persistent, training should be paused and campus sports medicine consulted.
                    </p>
                  </div>
                )}
              </div>

              <div className="flex space-x-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowCheckInModal(false)}
                  className="flex-1 py-2 border border-bordercolor text-dualtext-secondary text-xs font-semibold rounded-xl"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2 bg-primary hover:bg-primary-hover text-white text-xs font-semibold rounded-xl shadow-xs"
                >
                  Record Check-In
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
