import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { Phone, Lock, LogIn, UserCheck, Sparkles, AlertCircle } from 'lucide-react';

interface LoginPageProps {
  onSuccess: () => void;
  onNavigateRegister: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSuccess, onNavigateRegister }) => {
  const { login } = useAuth();
  const { t } = useLanguage();
  const [phone, setPhone] = useState('9811122233');
  const [password, setPassword] = useState('Password123');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await login(phone, password);
      onSuccess();
    } catch (err: any) {
      setError(err.message || 'Login failed. Please check your credentials.');
    } finally {
      setSubmitting(false);
    }
  };

  const setDemoCredentials = (demoPhone: string) => {
    setPhone(demoPhone);
    setPassword('Password123');
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center p-4">
      <div className="bg-white max-w-md w-full rounded-3xl shadow-xl border border-amber-100 p-8 space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-amber-500 text-amber-950 font-black text-3xl shadow-md mb-2">
            क
          </div>
          <h1 className="text-2xl font-extrabold text-amber-950">{t.login}</h1>
          <p className="text-sm text-slate-500">{t.tagline}</p>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-xl flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <p className="text-xs font-semibold text-red-700">{error}</p>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              {t.phone}
            </label>
            <div className="relative">
              <Phone className="w-5 h-5 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="text"
                required
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="e.g. 9811122233"
                className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 font-medium text-sm text-slate-900"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
              {t.password}
            </label>
            <div className="relative">
              <Lock className="w-5 h-5 text-slate-400 absolute left-3.5 top-3" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full pl-11 pr-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-amber-500 focus:border-amber-500 font-medium text-sm text-slate-900"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3.5 px-4 bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white font-bold rounded-xl shadow-md transition-all flex items-center justify-center gap-2 text-base active:scale-95 disabled:opacity-50"
          >
            <LogIn className="w-5 h-5" />
            {submitting ? 'Logging In...' : t.login}
          </button>
        </form>

        {/* Quick Demo Switcher */}
        <div className="border-t border-slate-100 pt-5 space-y-3">
          <div className="flex items-center gap-1.5 text-xs font-bold text-amber-800">
            <Sparkles className="w-4 h-4 text-amber-500" />
            <span>{t.quickDemo}</span>
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => setDemoCredentials('9811122233')}
              className="p-2 bg-amber-50 hover:bg-amber-100 border border-amber-200 rounded-lg text-center transition-all"
            >
              <span className="block text-xs font-bold text-amber-900">Sunita Devi</span>
              <span className="text-[10px] text-amber-700">Artisan</span>
            </button>
            <button
              type="button"
              onClick={() => setDemoCredentials('9844455566')}
              className="p-2 bg-indigo-50 hover:bg-indigo-100 border border-indigo-200 rounded-lg text-center transition-all"
            >
              <span className="block text-xs font-bold text-indigo-900">FabIndia</span>
              <span className="text-[10px] text-indigo-700">Buyer</span>
            </button>
            <button
              type="button"
              onClick={() => setDemoCredentials('9876543210')}
              className="p-2 bg-emerald-50 hover:bg-emerald-100 border border-emerald-200 rounded-lg text-center transition-all"
            >
              <span className="block text-xs font-bold text-emerald-900">Admin</span>
              <span className="text-[10px] text-emerald-700">Manager</span>
            </button>
          </div>
        </div>

        {/* Footer Link */}
        <div className="text-center pt-2">
          <p className="text-xs text-slate-500">
            Don't have an account?{' '}
            <button
              onClick={onNavigateRegister}
              className="text-amber-700 font-bold hover:underline inline-flex items-center gap-1"
            >
              <UserCheck className="w-3.5 h-3.5" />
              {t.register}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};
