import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { ShieldCheck, UserCheck, ArrowRight, Activity, BookOpen, Moon } from 'lucide-react';

export const AuthPage: React.FC = () => {
  const { login, register } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      if (isLogin) {
        await login(email, password);
      } else {
        if (!fullName.trim()) {
          throw new Error('Please enter your full name');
        }
        if (password.length < 12) {
          throw new Error('Password must be at least 12 characters long');
        }
        await register(email, password, fullName);
      }
    } catch (err: any) {
      setError(
        err.response?.data?.detail || err.message || 'Authentication failed. Please verify your credentials.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async () => {
    setError(null);
    setLoading(true);
    try {
      await login('alex.morgan@dualwell.edu', 'DualWell2026!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Demo login failed. Make sure backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-dualbg flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      {/* Brand Header */}
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <div className="inline-flex w-14 h-14 rounded-2xl bg-primary items-center justify-center text-white font-bold text-2xl shadow-md mb-3">
          DW
        </div>
        <h2 className="text-3xl font-extrabold text-dualtext-primary tracking-tight">
          Dual<span className="text-primary">Well</span>
        </h2>
        <p className="mt-1 text-sm text-dualtext-secondary max-w-sm mx-auto">
          Smart Student Wellness and Academic Performance System
        </p>

        {/* Value pills */}
        <div className="flex items-center justify-center space-x-2 mt-4 text-[11px] font-semibold text-dualtext-secondary">
          <span className="flex items-center space-x-1 bg-white border border-bordercolor px-2.5 py-1 rounded-full">
            <BookOpen className="w-3.5 h-3.5 text-primary" />
            <span>Academic Load</span>
          </span>
          <span className="flex items-center space-x-1 bg-white border border-bordercolor px-2.5 py-1 rounded-full">
            <Activity className="w-3.5 h-3.5 text-risk-green" />
            <span>Athletic Demands</span>
          </span>
          <span className="flex items-center space-x-1 bg-white border border-bordercolor px-2.5 py-1 rounded-full">
            <Moon className="w-3.5 h-3.5 text-indigo-500" />
            <span>Restorative Sleep</span>
          </span>
        </div>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-6 shadow-sm border border-bordercolor rounded-2xl sm:px-10">
          {/* Quick Demo Login Banner */}
          <div className="mb-6 bg-primary-soft border border-primary/20 rounded-xl p-3.5">
            <div className="flex items-center justify-between mb-1">
              <span className="text-xs font-bold text-primary flex items-center space-x-1">
                <UserCheck className="w-4 h-4" />
                <span>Instant Demo Access</span>
              </span>
              <span className="text-[10px] bg-primary text-white font-bold px-2 py-0.5 rounded-full">
                Collegiate Athlete
              </span>
            </div>
            <p className="text-xs text-dualtext-secondary mb-2.5">
              Experience DualWell populated with student <strong>Alex Morgan</strong> (CS Major & Collegiate Rowing Athlete).
            </p>
            <button
              type="button"
              onClick={handleDemoLogin}
              disabled={loading}
              className="w-full flex items-center justify-center space-x-2 bg-primary hover:bg-primary-hover text-white text-xs font-semibold py-2 px-3 rounded-lg shadow-sm transition-colors"
            >
              <span>One-Click Login as Alex Morgan</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-bordercolor" />
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="px-3 bg-white text-dualtext-secondary">or sign in with credentials</span>
            </div>
          </div>

          {/* Tab Selector */}
          <div className="flex border-b border-bordercolor mb-6">
            <button
              onClick={() => { setIsLogin(true); setError(null); }}
              className={`flex-1 py-2 text-sm font-semibold text-center border-b-2 transition-colors ${
                isLogin
                  ? 'border-primary text-primary'
                  : 'border-transparent text-dualtext-secondary hover:text-dualtext-primary'
              }`}
            >
              Sign In
            </button>
            <button
              onClick={() => { setIsLogin(false); setError(null); }}
              className={`flex-1 py-2 text-sm font-semibold text-center border-b-2 transition-colors ${
                !isLogin
                  ? 'border-primary text-primary'
                  : 'border-transparent text-dualtext-secondary hover:text-dualtext-primary'
              }`}
            >
              Create Account
            </button>
          </div>

          {error && (
            <div className="mb-4 bg-red-50 border border-red-200 text-risk-red text-xs p-3 rounded-xl">
              {error}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            {!isLogin && (
              <div>
                <label className="block text-xs font-medium text-dualtext-primary">
                  Full Name
                </label>
                <input
                  type="text"
                  required
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  placeholder="e.g. Jordan Lee"
                  className="mt-1 block w-full px-3 py-2 border border-bordercolor rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                />
              </div>
            )}

            <div>
              <label className="block text-xs font-medium text-dualtext-primary">
                Student Email
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="athlete@university.edu"
                className="mt-1 block w-full px-3 py-2 border border-bordercolor rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-xs font-medium text-dualtext-primary">
                Password
              </label>
              <input
                type="password"
                required
                minLength={isLogin ? undefined : 12}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="mt-1 block w-full px-3 py-2 border border-bordercolor rounded-xl text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
              {!isLogin && (
                <p className="mt-1 text-[11px] text-dualtext-secondary">
                  At least 12 characters.
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-xl shadow-sm text-sm font-semibold text-white bg-dualtext-primary hover:bg-black focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors disabled:opacity-50"
            >
              {loading ? 'Processing...' : isLogin ? 'Sign In to DualWell' : 'Complete Registration'}
            </button>
          </form>

          <div className="mt-6 flex items-center justify-center space-x-2 text-[11px] text-dualtext-secondary">
            <ShieldCheck className="w-4 h-4 text-dualtext-secondary" />
            <span>Encrypted JWT Authentication & Local Data Sovereignty</span>
          </div>
        </div>
      </div>
    </div>
  );
};
