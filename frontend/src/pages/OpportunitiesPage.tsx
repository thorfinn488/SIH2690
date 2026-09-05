import React, { useEffect, useState } from 'react';
import { OpportunityListItem } from '../types';
import { apiRequest } from '../api/client';
import { Building2, MapPin, ShieldCheck, Sparkles } from 'lucide-react';
import { useLanguage } from '../context/LanguageContext';

export const OpportunitiesPage: React.FC = () => {
  const { t } = useLanguage();
  const [opportunities, setOpportunities] = useState<OpportunityListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadOpps() {
      try {
        const data = await apiRequest<OpportunityListItem[]>('/opportunities');
        setOpportunities(data || []);
      } catch (err) {
        console.error('Failed to load opportunities:', err);
      } finally {
        setLoading(false);
      }
    }
    loadOpps();
  }, []);

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 space-y-6">
      <div className="bg-gradient-to-r from-indigo-900 to-indigo-950 p-8 rounded-3xl text-white shadow-xl flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="space-y-2">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/20 text-indigo-300 text-xs font-semibold border border-indigo-500/30">
            <Sparkles className="w-3.5 h-3.5" /> Direct B2B Market Linkage
          </div>
          <h1 className="text-3xl font-extrabold text-indigo-100">{t.opportunities}</h1>
          <p className="text-xs text-indigo-200/80 max-w-xl">
            Connect directly with verified retail enterprises, export buyers, and boutique stores looking for authentic Indian handicraft products.
          </p>
        </div>
      </div>

      {loading ? (
        <div className="text-center py-20 text-slate-400">Loading buyer opportunities...</div>
      ) : opportunities.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {opportunities.map((opp) => (
            <div key={opp.opportunity_id} className="bg-white p-6 rounded-2xl border border-indigo-100 shadow-md space-y-4 hover:shadow-lg transition-all">
              <div className="flex items-start justify-between">
                <div>
                  <span className="text-xs font-bold text-indigo-700 uppercase tracking-wider block">{opp.company_name}</span>
                  <h3 className="text-lg font-extrabold text-slate-900 mt-1">{opp.buyer_name}</h3>
                </div>
                <span className="px-3 py-1 bg-indigo-50 text-indigo-900 font-black text-sm rounded-full border border-indigo-200">
                  {opp.match_score}% Match
                </span>
              </div>

              <p className="text-xs text-slate-700 bg-slate-50 p-3.5 rounded-xl border border-slate-200 leading-relaxed font-medium">
                "{opp.requirement}"
              </p>

              <div className="flex items-center justify-between pt-2">
                <span className="text-xs font-semibold text-slate-500 flex items-center gap-1">
                  <MapPin className="w-3.5 h-3.5 text-indigo-500" /> Verified Procurement
                </span>
                <button className="px-4 py-2 bg-indigo-600 hover:bg-indigo-500 text-white font-bold text-xs rounded-xl shadow-sm transition-all flex items-center gap-1">
                  <ShieldCheck className="w-4 h-4" /> Send Quotation
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-slate-50 p-12 text-center rounded-3xl border-2 border-dashed border-slate-200 space-y-2">
          <Building2 className="w-12 h-12 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-700">No Open Buyer Opportunities</h3>
          <p className="text-xs text-slate-500">Check back soon for new retail buyer demands.</p>
        </div>
      )}
    </div>
  );
};
