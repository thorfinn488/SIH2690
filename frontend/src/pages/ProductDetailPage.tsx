import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { ProductDetail, Opportunity } from '../types';
import { apiRequest } from '../api/client';
import { ArrowLeft, Edit3, IndianRupee, Tag, Building2, MapPin, Sparkles, CheckCircle2, ShieldCheck, Volume2 } from 'lucide-react';

interface ProductDetailPageProps {
  productId: string;
  onBack: () => void;
}

export const ProductDetailPage: React.FC<ProductDetailPageProps> = ({ productId, onBack }) => {
  const { user } = useAuth();
  const { t } = useLanguage();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Catalogue edit modal state
  const [isEditing, setIsEditing] = useState(false);
  const [editName, setEditName] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function loadDetail() {
      try {
        const prodData = await apiRequest<ProductDetail>(`/products/${productId}`);
        setProduct(prodData);
        setEditName(prodData.catalogue?.name || '');
        setEditDesc(prodData.catalogue?.description || '');

        const oppData = await apiRequest<{ opportunities: Opportunity[] }>(`/products/${productId}/opportunities`);
        setOpportunities(oppData.opportunities || prodData.opportunities || []);
      } catch (err: any) {
        setError(err.message || 'Failed to load product details.');
      } finally {
        setLoading(false);
      }
    }
    loadDetail();
  }, [productId]);

  const handleSaveCatalogue = async () => {
    setSaving(true);
    try {
      await apiRequest(`/products/${productId}/catalogue`, {
        method: 'PUT',
        body: JSON.stringify({
          name: editName,
          description: editDesc,
        }),
      });

      // Reload product
      const updated = await apiRequest<ProductDetail>(`/products/${productId}`);
      setProduct(updated);
      setIsEditing(false);
    } catch (err: any) {
      alert('Failed to update catalogue: ' + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className="text-center py-20 text-slate-400">Loading product details...</div>;
  if (error || !product) return <div className="text-center py-20 text-red-500 font-bold">{error || 'Product not found'}</div>;

  const priceObj = product.price || {
    suggested_price: product.pricing?.suggested_price || 0,
    price_range: [product.pricing?.price_range_low || 0, product.pricing?.price_range_high || 0] as [number, number],
    explanation: product.pricing?.explanation || '',
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-8">
      {/* Back Header */}
      <button
        onClick={onBack}
        className="inline-flex items-center gap-2 text-amber-900 font-extrabold text-sm hover:text-amber-700 bg-amber-100/60 px-4 py-2 rounded-xl transition-all"
      >
        <ArrowLeft className="w-4 h-4" /> Back to Dashboard
      </button>

      {/* Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column: Image & Audio */}
        <div className="space-y-6">
          <div className="bg-white rounded-3xl border border-amber-200 overflow-hidden shadow-lg">
            {product.image_url ? (
              <img
                src={product.image_url}
                alt={product.catalogue?.name}
                className="w-full h-80 object-cover"
                onError={(event) => {
                  event.currentTarget.style.display = 'none';
                }}
              />
            ) : (
              <div className="h-80 bg-amber-50 flex items-center justify-center text-amber-400 font-bold">No Image</div>
            )}
            <div className="p-4 bg-amber-50/50 flex items-center justify-between">
              <span className="text-xs font-extrabold uppercase text-slate-500">Status</span>
              <span className="px-3 py-1 bg-emerald-500 text-white rounded-full text-xs font-bold">{product.status}</span>
            </div>
          </div>

          {product.audio && product.audio.length > 0 && (
            <div className="bg-white p-5 rounded-2xl border border-amber-200 shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-amber-900 font-bold text-sm">
                <Volume2 className="w-5 h-5 text-amber-600" />
                <span>Original Artisan Voice Note</span>
              </div>
              <audio controls src={product.audio[0].url} className="w-full h-10" />
            </div>
          )}
        </div>

        {/* Right Column: Catalogue & Pricing Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Catalogue Overview Card */}
          <div className="bg-white rounded-3xl border border-amber-200 p-6 sm:p-8 shadow-md space-y-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-amber-700">{product.catalogue?.category}</span>
                <h1 className="text-2xl sm:text-3xl font-extrabold text-amber-950 mt-1">{product.catalogue?.name}</h1>
              </div>

              {(user?.role === 'ARTISAN' || user?.role === 'ADMIN') && (
                <button
                  onClick={() => setIsEditing(true)}
                  className="px-3 py-2 bg-amber-100 hover:bg-amber-200 text-amber-900 font-bold rounded-xl text-xs flex items-center gap-1.5 transition-all shrink-0"
                >
                  <Edit3 className="w-4 h-4" /> Edit Catalogue
                </button>
              )}
            </div>

            <p className="text-sm text-slate-700 leading-relaxed bg-amber-50/50 p-4 rounded-2xl border border-amber-100">
              {product.catalogue?.description}
            </p>

            <div className="flex flex-wrap gap-2 pt-2">
              <span className="px-3 py-1 bg-amber-100 text-amber-900 font-bold text-xs rounded-full border border-amber-200">
                Craft: {product.catalogue?.craft}
              </span>
              <span className="px-3 py-1 bg-amber-100 text-amber-900 font-bold text-xs rounded-full border border-amber-200">
                Material: {product.catalogue?.material}
              </span>
              {product.catalogue?.tags?.map((tag, idx) => (
                <span key={idx} className="px-3 py-1 bg-slate-100 text-slate-700 font-semibold text-xs rounded-full flex items-center gap-1">
                  <Tag className="w-3 h-3 text-slate-400" /> #{tag}
                </span>
              ))}
            </div>
          </div>

          {/* Fair Pricing Card */}
          <div className="bg-gradient-to-br from-amber-50 to-amber-100/50 rounded-3xl border-2 border-amber-400 p-6 sm:p-8 shadow-md space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-amber-950 font-extrabold text-lg">
                <Sparkles className="w-5 h-5 text-amber-600" />
                <span>AI Fair Pricing Engine (उचित मूल्य निर्धारण)</span>
              </div>
              <span className="text-xs font-bold bg-amber-200 text-amber-900 px-3 py-1 rounded-full border border-amber-300">
                25% Artisan Margin
              </span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-white p-5 rounded-2xl border border-amber-200 shadow-sm">
              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">{t.suggestedPrice}</span>
                <div className="flex items-center text-3xl font-black text-amber-900 mt-1">
                  <IndianRupee className="w-7 h-7 text-amber-600" />
                  <span>{priceObj.suggested_price.toLocaleString('en-IN')}</span>
                </div>
              </div>

              <div>
                <span className="text-xs font-bold text-slate-400 uppercase tracking-wider block">{t.priceRange}</span>
                <div className="flex items-center text-lg font-bold text-slate-700 mt-2">
                  <span>₹{priceObj.price_range[0]?.toLocaleString('en-IN')} - ₹{priceObj.price_range[1]?.toLocaleString('en-IN')}</span>
                </div>
              </div>
            </div>

            <p className="text-xs text-slate-700 bg-white/80 p-4 rounded-xl border border-amber-200 leading-relaxed italic">
              "{priceObj.explanation}"
            </p>
          </div>

          {/* Buyer Opportunities Section */}
          <div className="bg-white rounded-3xl border border-amber-200 p-6 sm:p-8 shadow-md space-y-4">
            <div className="flex items-center gap-2 text-amber-950 font-extrabold text-xl">
              <Building2 className="w-6 h-6 text-amber-600" />
              <span>{t.matchingBuyers} ({opportunities.length})</span>
            </div>

            {opportunities.length > 0 ? (
              <div className="space-y-3">
                {opportunities.map((opp, idx) => (
                  <div key={idx} className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 hover:bg-amber-50/40 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-slate-900 text-sm">{opp.buyer_name}</span>
                        <span className="px-2 py-0.5 bg-emerald-100 text-emerald-800 text-[10px] font-bold rounded-full flex items-center gap-1">
                          <ShieldCheck className="w-3 h-3 text-emerald-600" /> Verified
                        </span>
                      </div>
                      <p className="text-xs text-slate-600 font-medium">{opp.requirement}</p>
                      <span className="text-[10px] text-slate-400 flex items-center gap-1">
                        <MapPin className="w-3 h-3" /> {opp.location}
                      </span>
                    </div>

                    <div className="flex items-center gap-3 shrink-0">
                      <div className="text-right">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block">Match Score</span>
                        <span className="text-base font-black text-amber-700">{opp.match_score}%</span>
                      </div>
                      <button className="px-4 py-2 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-xl shadow-sm transition-all">
                        Connect Buyer
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-xs text-slate-400 italic">No buyer matches found yet.</p>
            )}
          </div>
        </div>
      </div>

      {/* Edit Catalogue Modal */}
      {isEditing && (
        <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-white max-w-lg w-full rounded-3xl p-6 sm:p-8 space-y-6 shadow-2xl border border-amber-200">
            <h3 className="text-xl font-extrabold text-amber-950">Edit AI Generated Catalogue</h3>

            <div className="space-y-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Product Name
                </label>
                <input
                  type="text"
                  value={editName}
                  onChange={(e) => setEditName(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-amber-500 font-medium text-sm text-slate-900"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-1.5">
                  Craft Story & Description
                </label>
                <textarea
                  rows={4}
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                  className="w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-amber-500 font-medium text-sm text-slate-900"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => setIsEditing(false)}
                className="px-4 py-2.5 text-xs font-bold text-slate-600 hover:text-slate-900"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={saving}
                onClick={handleSaveCatalogue}
                className="px-6 py-2.5 bg-amber-600 hover:bg-amber-500 text-white font-bold text-xs rounded-xl shadow-md transition-all"
              >
                {saving ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
