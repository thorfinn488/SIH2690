import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { DashboardSummary, InsightItem, ProductDetail } from '../types';
import { apiRequest } from '../api/client';
import { PlusCircle, Sparkles, CheckCircle2, Clock, FileText, ShoppingBag, ArrowRight, Tag, IndianRupee, Layers } from 'lucide-react';

interface DashboardPageProps {
  onAddProduct: () => void;
  onSelectProduct: (productId: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onAddProduct, onSelectProduct }) => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [insights, setInsights] = useState<InsightItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [sumData, insData] = await Promise.all([
          apiRequest<DashboardSummary>('/dashboard'),
          apiRequest<{ insights: InsightItem[] }>('/dashboard/insights'),
        ]);
        setSummary(sumData);
        setInsights(insData.insights || []);
      } catch (err) {
        console.error('Error loading dashboard data:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Welcome Banner */}
      <div className="bg-gradient-to-r from-amber-900 via-amber-800 to-amber-900 rounded-3xl p-8 text-white shadow-xl flex flex-col md:flex-row items-center justify-between gap-6 relative overflow-hidden">
        <div className="space-y-2 z-10">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-amber-500/20 text-amber-300 text-xs font-semibold border border-amber-500/30">
            <Sparkles className="w-3.5 h-3.5" /> Welcome Back, {user?.name}!
          </div>
          <h1 className="text-3xl sm:text-4xl font-extrabold tracking-tight text-amber-100">
            {t.appName} - {t.tagline}
          </h1>
          <p className="text-amber-200/80 text-sm max-w-xl">
            Upload your handicraft photo and voice note to automatically generate smart cataloguing, fair price recommendations, and direct buyer linkage.
          </p>
        </div>

        {(user?.role === 'ARTISAN' || user?.role === 'ADMIN') && (
          <button
            onClick={onAddProduct}
            className="z-10 bg-amber-500 hover:bg-amber-400 text-amber-950 font-extrabold px-6 py-4 rounded-2xl shadow-lg transition-all flex items-center gap-3 text-base active:scale-95 shrink-0"
          >
            <PlusCircle className="w-6 h-6" />
            <span>{t.addProduct}</span>
          </button>
        )}
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-2xl border border-amber-200/70 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-amber-600">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{t.totalProducts}</span>
            <Layers className="w-6 h-6" />
          </div>
          <div className="text-3xl font-extrabold text-slate-900">{summary?.total_products ?? 0}</div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-emerald-200/70 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-emerald-600">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{t.readyCatalogues}</span>
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div className="text-3xl font-extrabold text-emerald-700">{summary?.catalogue_status.ready ?? 0}</div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-amber-200/70 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-amber-600">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{t.processing}</span>
            <Clock className="w-6 h-6 animate-spin" />
          </div>
          <div className="text-3xl font-extrabold text-amber-700">{summary?.catalogue_status.processing ?? 0}</div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-2">
          <div className="flex items-center justify-between text-slate-500">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500">{t.drafts}</span>
            <FileText className="w-6 h-6" />
          </div>
          <div className="text-3xl font-extrabold text-slate-700">{summary?.catalogue_status.draft ?? 0}</div>
        </div>
      </div>

      {/* AI Market Insights Banner */}
      {insights.length > 0 && (
        <div className="bg-amber-100/60 border border-amber-300/80 rounded-2xl p-6 space-y-4">
          <div className="flex items-center gap-2 text-amber-900 font-extrabold text-base">
            <Sparkles className="w-5 h-5 text-amber-600" />
            <span>AI Market Linkage Insights (बाज़ार अंतर्दृष्टि)</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {insights.map((item, idx) => (
              <div key={idx} className="bg-white p-4 rounded-xl border border-amber-200 flex items-start gap-3 shadow-sm">
                <div className="p-2 rounded-lg bg-amber-50 text-amber-700 shrink-0 mt-0.5">
                  <Tag className="w-4 h-4" />
                </div>
                <p className="text-xs font-semibold text-slate-800 leading-relaxed">{item.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Catalogued Products Grid */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-extrabold text-amber-950 flex items-center gap-2">
            <ShoppingBag className="w-6 h-6 text-amber-600" />
            {t.products}
          </h2>
        </div>

        {loading ? (
          <div className="text-center py-12 text-slate-400">Loading catalogued products...</div>
        ) : summary?.recent_products && summary.recent_products.length > 0 ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {summary.recent_products.map((prod) => (
              <div
                key={prod.product_id || prod.id}
                onClick={() => onSelectProduct(prod.product_id || prod.id || '')}
                className="bg-white rounded-2xl border border-amber-200/80 shadow-md hover:shadow-xl transition-all cursor-pointer overflow-hidden group flex flex-col justify-between"
              >
                {/* Image Header */}
                <div className="h-48 bg-amber-50 relative overflow-hidden flex items-center justify-center">
                  {prod.image_url ? (
                    <img
                      src={prod.image_url}
                      alt={prod.catalogue?.name || 'Artisan product'}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      onError={(event) => {
                        event.currentTarget.style.display = 'none';
                      }}
                    />
                  ) : (
                    <div className="text-center text-amber-400 p-4">
                      <ShoppingBag className="w-12 h-12 mx-auto mb-2 opacity-50" />
                      <span className="text-xs font-semibold">No Image Uploaded</span>
                    </div>
                  )}
                  <span
                    className={`absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-bold shadow-md ${
                      prod.status === 'READY' || prod.status === 'PUBLISHED'
                        ? 'bg-emerald-500 text-white'
                        : prod.status === 'PROCESSING'
                        ? 'bg-amber-500 text-white animate-pulse'
                        : 'bg-slate-500 text-white'
                    }`}
                  >
                    {prod.status}
                  </span>
                </div>

                {/* Body Content */}
                <div className="p-5 space-y-3 flex-1 flex flex-col justify-between">
                  <div>
                    <h3 className="font-extrabold text-slate-900 text-base group-hover:text-amber-700 transition-colors line-clamp-1">
                      {prod.catalogue?.name || 'Draft Product'}
                    </h3>
                    <p className="text-xs font-medium text-slate-500 mt-1 line-clamp-2">
                      {prod.catalogue?.description || 'Pending voice AI catalogue generation...'}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-slate-100 flex items-center justify-between">
                    <div>
                      <span className="text-[10px] uppercase font-bold text-slate-400 block">{t.suggestedPrice}</span>
                      <div className="flex items-center text-amber-900 font-extrabold text-base">
                        <IndianRupee className="w-4 h-4 text-amber-600" />
                        <span>
                          {prod.price?.suggested_price
                            ? prod.price.suggested_price.toLocaleString('en-IN')
                            : prod.pricing?.suggested_price
                            ? prod.pricing.suggested_price.toLocaleString('en-IN')
                            : 'N/A'}
                        </span>
                      </div>
                    </div>

                    <span className="text-xs font-bold text-amber-700 group-hover:translate-x-1 transition-transform flex items-center gap-1">
                      View <ArrowRight className="w-4 h-4" />
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-amber-50/50 border-2 border-dashed border-amber-200 rounded-3xl p-12 text-center space-y-4">
            <ShoppingBag className="w-12 h-12 text-amber-400 mx-auto" />
            <h3 className="text-lg font-bold text-amber-950">No catalogued products yet</h3>
            <p className="text-xs text-amber-800 max-w-sm mx-auto">
              Start by taking a photo and speaking about your product craft!
            </p>
            <button
              onClick={onAddProduct}
              className="bg-amber-600 hover:bg-amber-500 text-white font-bold px-6 py-3 rounded-xl shadow-md transition-all inline-flex items-center gap-2 text-sm"
            >
              <PlusCircle className="w-5 h-5" />
              {t.addProduct}
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
