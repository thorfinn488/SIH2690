import React, { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { LanguageProvider } from './context/LanguageContext';
import { Navbar } from './components/Navbar';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { DashboardPage } from './pages/DashboardPage';
import { AddProductPage } from './pages/AddProductPage';
import { ProductDetailPage } from './pages/ProductDetailPage';
import { OpportunitiesPage } from './pages/OpportunitiesPage';
import { AdminPage } from './pages/AdminPage';

function MainApp() {
  const { user, loading } = useAuth();
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [selectedProductId, setSelectedProductId] = useState<string | null>(null);

  if (loading) {
    return (
      <div className="min-h-screen bg-amber-50/50 flex flex-col items-center justify-center p-4">
        <div className="w-16 h-16 rounded-full bg-amber-500 text-amber-950 flex items-center justify-center font-black text-2xl animate-spin mb-4">
          क
        </div>
        <p className="text-amber-900 font-bold text-sm">Loading KalaSaathi...</p>
      </div>
    );
  }

  if (!user) {
    if (currentTab === 'register') {
      return (
        <RegisterPage
          onSuccess={() => setCurrentTab('dashboard')}
          onNavigateLogin={() => setCurrentTab('login')}
        />
      );
    }
    return (
      <LoginPage
        onSuccess={() => setCurrentTab('dashboard')}
        onNavigateRegister={() => setCurrentTab('register')}
      />
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-amber-50/30 text-slate-800">
      <Navbar currentTab={currentTab} setCurrentTab={setCurrentTab} />

      <main className="flex-1 pb-16">
        {currentTab === 'dashboard' && (
          <DashboardPage
            onAddProduct={() => setCurrentTab('add-product')}
            onSelectProduct={(id) => {
              setSelectedProductId(id);
              setCurrentTab('product-detail');
            }}
          />
        )}

        {currentTab === 'add-product' && (
          <AddProductPage
            onComplete={(id) => {
              setSelectedProductId(id);
              setCurrentTab('product-detail');
            }}
            onCancel={() => setCurrentTab('dashboard')}
          />
        )}

        {currentTab === 'product-detail' && selectedProductId && (
          <ProductDetailPage
            productId={selectedProductId}
            onBack={() => setCurrentTab('dashboard')}
          />
        )}

        {currentTab === 'opportunities' && <OpportunitiesPage />}

        {currentTab === 'admin' && <AdminPage />}
      </main>

      <footer className="bg-amber-950 text-amber-200/60 text-xs py-6 border-t border-amber-900 text-center space-y-1">
        <p className="font-semibold text-amber-100">SIH 26090 — AI Business Manager for Marginalized Artisans</p>
        <p>Contract-First Architecture • Empowering Rural Artisans with Voice AI & Smart Market Linkage</p>
      </footer>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <LanguageProvider>
        <MainApp />
      </LanguageProvider>
    </AuthProvider>
  );
}
