import React, { useEffect, useState } from 'react';
import { apiRequest } from '../api/client';
import { ShieldCheck, Users, ShoppingBag, Building2, MapPin } from 'lucide-react';

export const AdminPage: React.FC = () => {
  const [artisans, setArtisans] = useState<any[]>([]);
  const [products, setProducts] = useState<any[]>([]);
  const [opportunities, setOpportunities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadAdminData() {
      try {
        const [artData, prodData, oppData] = await Promise.all([
          apiRequest<any[]>('/admin/artisans'),
          apiRequest<any[]>('/admin/products'),
          apiRequest<any[]>('/admin/opportunities'),
        ]);
        setArtisans(artData || []);
        setProducts(prodData || []);
        setOpportunities(oppData || []);
      } catch (err) {
        console.error('Admin data load error:', err);
      } finally {
        setLoading(false);
      }
    }
    loadAdminData();
  }, []);

  if (loading) return <div className="text-center py-20 text-slate-400">Loading admin panel...</div>;

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      <div className="bg-gradient-to-r from-emerald-900 to-emerald-950 p-8 rounded-3xl text-white shadow-xl flex items-center gap-4">
        <div className="p-3 bg-emerald-500/20 rounded-2xl border border-emerald-500/30">
          <ShieldCheck className="w-8 h-8 text-emerald-400" />
        </div>
        <div>
          <h1 className="text-2xl font-extrabold text-emerald-100">System Admin Dashboard</h1>
          <p className="text-xs text-emerald-200/80">Manage registered artisans, products, and procurement linkages.</p>
        </div>
      </div>

      {/* Artisans List */}
      <div className="bg-white rounded-3xl border border-emerald-100 p-6 shadow-md space-y-4">
        <h2 className="text-lg font-extrabold text-emerald-950 flex items-center gap-2">
          <Users className="w-5 h-5 text-emerald-600" /> Registered Artisans ({artisans.length})
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {artisans.map((art) => (
            <div key={art.artisan_id} className="p-4 rounded-2xl border border-slate-200 bg-slate-50/50 space-y-1">
              <span className="font-extrabold text-slate-900 text-sm block">{art.name}</span>
              <span className="text-xs text-slate-500 block font-medium">Craft: {art.craft_specialty}</span>
              <span className="text-[10px] text-slate-400 flex items-center gap-1">
                <MapPin className="w-3 h-3 text-emerald-600" /> {art.region} • Phone: {art.phone}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Products Overview */}
      <div className="bg-white rounded-3xl border border-amber-100 p-6 shadow-md space-y-4">
        <h2 className="text-lg font-extrabold text-amber-950 flex items-center gap-2">
          <ShoppingBag className="w-5 h-5 text-amber-600" /> Catalogued Products ({products.length})
        </h2>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-amber-50 text-amber-900 font-bold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="p-3">Product Name</th>
                <th className="p-3">Artisan</th>
                <th className="p-3">Status</th>
                <th className="p-3">Suggested Price</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {products.map((p) => (
                <tr key={p.product_id} className="hover:bg-amber-50/30">
                  <td className="p-3 font-extrabold text-slate-900">{p.catalogue_name || 'Draft Product'}</td>
                  <td className="p-3 font-semibold text-slate-700">{p.artisan_name}</td>
                  <td className="p-3">
                    <span className="px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-bold text-[10px]">
                      {p.status}
                    </span>
                  </td>
                  <td className="p-3 font-bold text-amber-900">₹{p.suggested_price ? p.suggested_price.toLocaleString('en-IN') : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
