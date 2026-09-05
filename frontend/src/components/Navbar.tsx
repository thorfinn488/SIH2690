import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { Sparkles, LogOut, Languages, User as UserIcon, PlusCircle, LayoutDashboard, ShoppingBag, ShieldCheck } from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ currentTab, setCurrentTab }) => {
  const { user, logout } = useAuth();
  const { language, setLanguage, t } = useLanguage();

  return (
    <header className="bg-gradient-to-r from-amber-800 via-amber-900 to-amber-950 text-white shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Branding */}
          <div 
            className="flex items-center gap-3 cursor-pointer select-none"
            onClick={() => setCurrentTab('dashboard')}
          >
            <div className="w-10 h-10 rounded-full bg-amber-500 text-amber-950 flex items-center justify-center font-black text-xl shadow-md">
              क
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-tight text-amber-100">{t.appName}</span>
                <span className="bg-amber-500/20 text-amber-300 text-xs px-2 py-0.5 rounded-full border border-amber-500/30 flex items-center gap-1 font-medium">
                  <Sparkles className="w-3 h-3 text-amber-400" /> AI Business Manager
                </span>
              </div>
              <p className="text-xs text-amber-200/80 hidden sm:block">{t.tagline}</p>
            </div>
          </div>

          {/* Navigation Links */}
          {user && (
            <nav className="hidden md:flex items-center gap-1">
              <button
                onClick={() => setCurrentTab('dashboard')}
                className={`px-3 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-1.5 ${
                  currentTab === 'dashboard' ? 'bg-amber-500/30 text-amber-200 border border-amber-500/40' : 'text-amber-100/80 hover:bg-amber-800/60'
                }`}
              >
                <LayoutDashboard className="w-4 h-4" />
                {t.dashboard}
              </button>

              {(user.role === 'ARTISAN' || user.role === 'ADMIN') && (
                <button
                  onClick={() => setCurrentTab('add-product')}
                  className={`px-3 py-2 rounded-lg font-semibold text-sm transition-all flex items-center gap-1.5 ${
                    currentTab === 'add-product' ? 'bg-amber-500 text-amber-950 shadow-md' : 'bg-amber-600 hover:bg-amber-500 text-white'
                  }`}
                >
                  <PlusCircle className="w-4 h-4" />
                  {t.addProduct}
                </button>
              )}

              <button
                onClick={() => setCurrentTab('opportunities')}
                className={`px-3 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-1.5 ${
                  currentTab === 'opportunities' ? 'bg-amber-500/30 text-amber-200 border border-amber-500/40' : 'text-amber-100/80 hover:bg-amber-800/60'
                }`}
              >
                <ShoppingBag className="w-4 h-4" />
                {t.opportunities}
              </button>

              {user.role === 'ADMIN' && (
                <button
                  onClick={() => setCurrentTab('admin')}
                  className={`px-3 py-2 rounded-lg font-medium text-sm transition-all flex items-center gap-1.5 ${
                    currentTab === 'admin' ? 'bg-amber-500/30 text-amber-200 border border-amber-500/40' : 'text-amber-100/80 hover:bg-amber-800/60'
                  }`}
                >
                  <ShieldCheck className="w-4 h-4" />
                  Admin Panel
                </button>
              )}
            </nav>
          )}

          {/* User Controls & Language Toggle */}
          <div className="flex items-center gap-3">
            {/* Language Switcher */}
            <button
              onClick={() => setLanguage(language === 'en' ? 'hi' : 'en')}
              className="bg-amber-800/80 hover:bg-amber-700 text-amber-100 px-3 py-1.5 rounded-lg border border-amber-600/40 text-xs font-semibold flex items-center gap-1.5 transition-all"
            >
              <Languages className="w-4 h-4 text-amber-300" />
              <span>{language === 'en' ? 'हिंदी' : 'English'}</span>
            </button>

            {user ? (
              <div className="flex items-center gap-3 pl-2 border-l border-amber-700/60">
                <div className="hidden sm:flex flex-col text-right">
                  <span className="text-xs font-bold text-amber-100">{user.name}</span>
                  <span className="text-[10px] text-amber-300/80 font-mono uppercase">{user.role}</span>
                </div>
                <button
                  onClick={logout}
                  title={t.logout}
                  className="p-2 text-amber-200/80 hover:text-white hover:bg-amber-800 rounded-lg transition-all"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </div>
            ) : (
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentTab('login')}
                  className="text-amber-100 hover:text-white px-3 py-1.5 text-xs font-semibold rounded-lg hover:bg-amber-800/50"
                >
                  {t.login}
                </button>
                <button
                  onClick={() => setCurrentTab('register')}
                  className="bg-amber-500 hover:bg-amber-400 text-amber-950 font-bold px-3 py-1.5 text-xs rounded-lg shadow-sm"
                >
                  {t.register}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
