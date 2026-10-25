import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';
import {
  Watch,
  Heart,
  Activity,
  Moon,
  RefreshCw,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  Shield,
  Smartphone,
  Cpu
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';

export const WearableMonitoringPage: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [statusData, setStatusData] = useState<any>(null);
  const [providers, setProviders] = useState<any[]>([]);
  const [observations, setObservations] = useState<any[]>([]);
  const [activeMetricTab, setActiveMetricTab] = useState<'heart_rate' | 'hrv' | 'steps'>('heart_rate');
  const [selectedProviderModal, setSelectedProviderModal] = useState<any | null>(null);

  const fetchWearableData = async () => {
    try {
      setLoading(true);
      const [statusRes, provRes, obsRes] = await Promise.all([
        apiClient.get('/wearable/status'),
        apiClient.get('/wearable/providers'),
        apiClient.get('/wearable/observations?limit=40')
      ]);
      setStatusData(statusRes.data);
      setProviders(provRes.data || []);
      setObservations(obsRes.data || []);
    } catch (err) {
      console.error('Failed to load wearable data:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWearableData();
  }, []);

  const handleSync = async (providerId: string = 'demo') => {
    try {
      setSyncing(true);
      await apiClient.post('/wearable/sync', { provider: providerId });
      await fetchWearableData();
    } catch (err) {
      console.error('Wearable sync error:', err);
    } finally {
      setSyncing(false);
    }
  };

  const handleConnect = async (providerId: string) => {
    try {
      await apiClient.post(`/wearable/connect/${providerId}`);
      await fetchWearableData();
    } catch (err) {
      console.error('Connect failed:', err);
    }
  };

  const handleDisconnect = async (providerId: string) => {
    try {
      await apiClient.post(`/wearable/disconnect/${providerId}`);
      await fetchWearableData();
    } catch (err) {
      console.error('Disconnect failed:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="w-8 h-8 border-4 border-primary/30 border-t-primary rounded-full animate-spin" />
      </div>
    );
  }

  // Filter observations by active metric
  const filteredObs = observations
    .filter((o) => o.metric_type === activeMetricTab)
    .map((o) => ({
      time: new Date(o.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      value: o.value,
      source: o.data_source,
    }))
    .reverse();

  return (
    <div className="space-y-6 pb-12">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-dualtext-primary">
            Wearable Monitoring & Device Telemetry
          </h2>
          <p className="text-xs sm:text-sm text-dualtext-secondary">
            Modular smartwatch integration for autonomic nervous system monitoring and physical strain tracking.
          </p>
        </div>

        <button
          onClick={() => handleSync('demo')}
          disabled={syncing}
          className="flex items-center space-x-2 bg-primary hover:bg-primary-hover text-white text-xs sm:text-sm font-semibold px-4 py-2 rounded-xl shadow-xs transition-colors self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${syncing ? 'animate-spin' : ''}`} />
          <span>{syncing ? 'Polling Telemetry...' : 'Poll Live Telemetry'}</span>
        </button>
      </div>

      {/* Integration Reality Notice */}
      <div className="bg-primary-soft/60 border border-primary/20 rounded-2xl p-4 flex items-start space-x-3 text-xs text-dualtext-secondary leading-relaxed">
        <Shield className="w-5 h-5 text-primary shrink-0 mt-0.5" />
        <div>
          <strong className="text-dualtext-primary">Wearable Architecture Disclosure:</strong> Web browsers cannot connect directly to low-level Bluetooth or proprietary smartwatch sensors without supported vendor cloud APIs or native companion apps. DualWell provides a high-fidelity local athlete simulator alongside real provider specifications for Fitbit, Apple Health, and Wear OS Health Connect.
        </div>
      </div>

      {/* Provider Cards Grid */}
      <div>
        <h3 className="text-sm font-bold text-dualtext-primary mb-3">
          Supported Wearable Provider Ecosystems
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {providers.map((p) => {
            const isConn = statusData?.connections?.some(
              (c: any) => c.provider === p.provider_id && c.is_connected
            );
            return (
              <div
                key={p.provider_id}
                className={`bg-white rounded-2xl border p-5 flex flex-col justify-between transition-all ${
                  isConn ? 'border-primary/40 shadow-xs' : 'border-bordercolor'
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-3">
                    <span className="p-2 rounded-xl bg-dualbg text-primary">
                      {p.provider_id === 'apple_health' ? (
                        <Smartphone className="w-5 h-5 text-gray-800" />
                      ) : p.provider_id === 'demo' ? (
                        <Cpu className="w-5 h-5 text-primary" />
                      ) : (
                        <Watch className="w-5 h-5 text-dualtext-primary" />
                      )}
                    </span>
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full ${
                        p.availability === 'coming_soon'
                          ? 'bg-cream text-risk-yellow border border-amber-200'
                          : isConn
                          ? 'bg-mint text-risk-green border border-emerald-200'
                          : 'bg-dualbg text-dualtext-secondary'
                      }`}
                    >
                      {p.availability === 'coming_soon'
                        ? 'COMING SOON'
                        : isConn
                        ? 'CONNECTED'
                        : 'DISCONNECTED'}
                    </span>
                  </div>

                  <h4 className="font-bold text-sm text-dualtext-primary mb-1">
                    {p.display_name}
                  </h4>
                  <p className="text-[11px] text-dualtext-secondary line-clamp-2 mb-3">
                    {p.technical_details?.requirements || 'Biometric sensor synchronization.'}
                  </p>

                  <div className="flex flex-wrap gap-1 mb-4">
                    {p.supported_metrics?.map((m: string) => (
                      <span
                        key={m}
                        className="text-[10px] bg-dualbg px-2 py-0.5 rounded font-mono text-dualtext-secondary"
                      >
                        {m}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="space-y-2 pt-3 border-t border-bordercolor">
                  {isConn ? (
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleSync(p.provider_id)}
                        disabled={syncing}
                        className="flex-1 py-1.5 px-3 bg-dualbg hover:bg-primary-soft text-dualtext-primary hover:text-primary text-xs font-semibold rounded-lg transition-colors"
                      >
                        Sync
                      </button>
                      <button
                        onClick={() => handleDisconnect(p.provider_id)}
                        className="py-1.5 px-3 border border-bordercolor text-dualtext-secondary hover:text-risk-red text-xs rounded-lg transition-colors"
                      >
                        Disconnect
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleConnect(p.provider_id)}
                      disabled={p.availability === 'coming_soon'}
                      className={`w-full py-1.5 px-3 text-xs font-semibold rounded-lg transition-colors ${
                        p.availability === 'coming_soon'
                          ? 'bg-dualbg text-dualtext-secondary cursor-not-allowed'
                          : 'bg-dualtext-primary hover:bg-black text-white'
                      }`}
                    >
                      {p.availability === 'coming_soon' ? 'Coming Soon' : 'Connect Provider'}
                    </button>
                  )}

                  <button
                    onClick={() => setSelectedProviderModal(p)}
                    className="w-full text-center text-[11px] text-primary hover:underline block pt-1"
                  >
                    View Setup Instructions & API Specs
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Telemetry Metric Tabs & Chart */}
      <div className="bg-white rounded-2xl border border-bordercolor p-5 shadow-xs">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
          <div>
            <h3 className="text-sm font-bold text-dualtext-primary">
              Telemetry Stream & Historical Observations
            </h3>
            <p className="text-xs text-dualtext-secondary">
              Continuous sampling of physiological variables with explicit source provenance tags.
            </p>
          </div>

          <div className="flex items-center space-x-1 bg-dualbg p-1 rounded-xl">
            {(['heart_rate', 'hrv', 'steps'] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveMetricTab(tab)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold capitalize transition-all ${
                  activeMetricTab === tab
                    ? 'bg-white text-primary shadow-xs'
                    : 'text-dualtext-secondary hover:text-dualtext-primary'
                }`}
              >
                {tab.replace('_', ' ')}
              </button>
            ))}
          </div>
        </div>

        {filteredObs.length > 0 ? (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={filteredObs} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="metricGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4F7DF3" stopOpacity={0.25} />
                    <stop offset="95%" stopColor="#4F7DF3" stopOpacity={0.0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#F1F5F9" vertical={false} />
                <XAxis dataKey="time" stroke="#94A3B8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94A3B8" fontSize={11} tickLine={false} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#FFFFFF',
                    borderRadius: '12px',
                    border: '1px solid #E5E9F2',
                    fontSize: '12px',
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="#4F7DF3"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#metricGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="p-8 text-center text-xs text-dualtext-secondary">
            No telemetry observations available for {activeMetricTab}. Click "Poll Live Telemetry" above.
          </div>
        )}
      </div>

      {/* Observation Table with Provenance Tagging */}
      <div className="bg-white rounded-2xl border border-bordercolor overflow-hidden shadow-xs">
        <div className="p-4 sm:p-5 border-b border-bordercolor">
          <h3 className="text-sm font-bold text-dualtext-primary">
            Recent Telemetry Observations Log
          </h3>
          <p className="text-xs text-dualtext-secondary">
            Verified duplicate prevention enforced at database layer.
          </p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-dualbg/70 text-dualtext-secondary uppercase text-[10px] tracking-wider border-b border-bordercolor">
              <tr>
                <th className="px-5 py-3 font-semibold">Timestamp</th>
                <th className="px-5 py-3 font-semibold">Metric</th>
                <th className="px-5 py-3 font-semibold">Measurement</th>
                <th className="px-5 py-3 font-semibold">Provenance Tag</th>
                <th className="px-5 py-3 font-semibold">Contextual Metadata</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-bordercolor">
              {observations.slice(0, 10).map((obs) => (
                <tr key={obs.id} className="hover:bg-dualbg/30 transition-colors">
                  <td className="px-5 py-3 font-mono text-dualtext-secondary">
                    {new Date(obs.recorded_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </td>
                  <td className="px-5 py-3 font-semibold text-dualtext-primary capitalize">
                    {obs.metric_type.replace('_', ' ')}
                  </td>
                  <td className="px-5 py-3 font-bold text-dualtext-primary">
                    {obs.value} <span className="text-[10px] font-normal text-dualtext-secondary">{obs.unit}</span>
                  </td>
                  <td className="px-5 py-3">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wider ${
                        obs.data_source === 'WEARABLE_LIVE'
                          ? 'bg-mint text-risk-green border border-emerald-200'
                          : obs.data_source === 'SIMULATED_DEMO'
                          ? 'bg-primary-soft text-primary border border-primary/20'
                          : 'bg-cream text-risk-yellow border border-amber-200'
                      }`}
                    >
                      {obs.data_source.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-5 py-3 text-dualtext-secondary truncate max-w-xs">
                    {obs.extra_metadata || 'Standard interval sampling'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Provider Detail Modal */}
      {selectedProviderModal && (
        <div className="fixed inset-0 bg-black/30 z-50 flex items-center justify-center p-4 backdrop-blur-xs">
          <div className="bg-white rounded-2xl max-w-lg w-full p-6 border border-bordercolor shadow-xl">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-dualtext-primary">
                {selectedProviderModal.display_name} — Integration Spec
              </h3>
              <button
                onClick={() => setSelectedProviderModal(null)}
                className="text-dualtext-secondary hover:text-dualtext-primary text-sm font-bold"
              >
                ✕
              </button>
            </div>

            <div className="space-y-3 text-xs text-dualtext-secondary leading-relaxed">
              <div>
                <strong className="text-dualtext-primary block mb-0.5">Integration Pattern:</strong>
                <p>{selectedProviderModal.technical_details?.type}</p>
              </div>

              <div>
                <strong className="text-dualtext-primary block mb-0.5">Authorization & Security:</strong>
                <p>{selectedProviderModal.technical_details?.authorization}</p>
              </div>

              {selectedProviderModal.technical_details?.setup_steps && (
                <div>
                  <strong className="text-dualtext-primary block mb-1">Connection Steps:</strong>
                  <ol className="list-decimal list-inside space-y-1 bg-dualbg p-3 rounded-xl border border-bordercolor font-mono text-[11px]">
                    {selectedProviderModal.technical_details.setup_steps.map((st: string, idx: number) => (
                      <li key={idx}>{st}</li>
                    ))}
                  </ol>
                </div>
              )}
            </div>

            <button
              onClick={() => setSelectedProviderModal(null)}
              className="mt-6 w-full py-2 bg-dualtext-primary text-white font-semibold text-xs rounded-xl"
            >
              Close Specification
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
