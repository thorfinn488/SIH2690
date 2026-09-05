import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useLanguage } from '../context/LanguageContext';
import { AudioRecorder } from '../components/AudioRecorder';
import { apiRequest } from '../api/client';
import { ProductCreateResponse, UploadImageResponse, UploadAudioResponse, ProcessProductResponse, ProcessingStatusData, ProductDetail } from '../types';
import { Camera, Upload, ArrowRight, Sparkles, CheckCircle2, RefreshCw, AlertCircle, IndianRupee } from 'lucide-react';

interface AddProductPageProps {
  onComplete: (productId: string) => void;
  onCancel: () => void;
}

export const AddProductPage: React.FC<AddProductPageProps> = ({ onComplete, onCancel }) => {
  const { t } = useLanguage();
  const [step, setStep] = useState<'upload' | 'processing' | 'done'>('upload');
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [processingStatus, setProcessingStatus] = useState<ProcessingStatusData | null>(null);
  const [completedProduct, setCompletedProduct] = useState<ProductDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleStartPipeline = async () => {
    if (!imageFile) {
      setError('Please select or capture a product photo first.');
      return;
    }
    setError(null);
    setLoading(true);

    try {
      // 1. Create product draft
      const draft = await apiRequest<ProductCreateResponse>('/products', { method: 'POST' });
      const productId = draft.product_id;

      // 2. Upload image
      const formDataImage = new FormData();
      formDataImage.append('file', imageFile);
      await apiRequest<UploadImageResponse>(`/products/${productId}/image`, {
        method: 'POST',
        body: formDataImage,
      });

      // 3. Upload audio if present
      if (audioBlob) {
        const formDataAudio = new FormData();
        formDataAudio.append('file', audioBlob, 'voice_note.mp3');
        await apiRequest<UploadAudioResponse>(`/products/${productId}/audio`, {
          method: 'POST',
          body: formDataAudio,
        });
      }

      // 4. Trigger processing
      await apiRequest<ProcessProductResponse>(`/products/${productId}/process`, { method: 'POST' });

      setStep('processing');
      pollProcessingStatus(productId);
    } catch (err: any) {
      setError(err.message || 'Failed to start AI cataloging pipeline.');
      setLoading(false);
    }
  };

  const pollProcessingStatus = (productId: string) => {
    const interval = setInterval(async () => {
      try {
        const statusData = await apiRequest<ProcessingStatusData>(`/products/${productId}/processing-status`);
        setProcessingStatus(statusData);

        if (statusData.status === 'READY' || statusData.status === 'PUBLISHED' || statusData.step === 'done') {
          clearInterval(interval);
          const fullProduct = await apiRequest<ProductDetail>(`/products/${productId}`);
          setCompletedProduct(fullProduct);
          setStep('done');
          setLoading(false);
        } else if (statusData.status === 'FAILED') {
          clearInterval(interval);
          setError('AI Pipeline processing failed. Please try again.');
          setStep('upload');
          setLoading(false);
        }
      } catch (err: any) {
        // If poll fails briefly, retry
      }
    }, 1500);
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-8">
      <div className="bg-white rounded-3xl shadow-xl border border-amber-200 p-6 sm:p-10 space-y-8">
        {/* Header */}
        <div className="text-center space-y-2 border-b border-amber-100 pb-6">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-amber-100 text-amber-900 text-xs font-bold border border-amber-300">
            <Sparkles className="w-4 h-4 text-amber-600" /> Smart AI Cataloguing & Pricing
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-amber-950">{t.addProduct}</h1>
          <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto">
            Take a photo and speak a voice note — our AI will generate a complete catalog description, market price, and find matching buyers!
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-xl flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <p className="text-xs font-semibold text-red-700">{error}</p>
          </div>
        )}

        {/* STEP 1: Upload Photo & Voice */}
        {step === 'upload' && (
          <div className="space-y-8">
            {/* Step 1: Photo Upload */}
            <div className="space-y-3">
              <label className="block text-sm font-extrabold text-amber-950 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-amber-600 text-white flex items-center justify-center text-xs font-bold">1</span>
                {t.photoStep}
              </label>

              {!imagePreview ? (
                <label className="border-3 border-dashed border-amber-300 bg-amber-50/50 hover:bg-amber-100/50 p-8 rounded-2xl flex flex-col items-center justify-center gap-3 cursor-pointer transition-all">
                  <div className="w-16 h-16 rounded-full bg-amber-500 text-amber-950 flex items-center justify-center shadow-lg">
                    <Camera className="w-8 h-8" />
                  </div>
                  <div className="text-center">
                    <span className="text-sm font-bold text-amber-900 block">Tap to select photo or take picture</span>
                    <span className="text-xs text-amber-700">JPEG, PNG, WEBP up to 10MB</span>
                  </div>
                  <input type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
                </label>
              ) : (
                <div className="relative rounded-2xl overflow-hidden border-2 border-amber-400 max-h-64 bg-amber-50 flex items-center justify-center">
                  <img src={imagePreview} alt="Product preview" className="max-h-64 object-contain" />
                  <label className="absolute bottom-3 right-3 bg-amber-900/80 text-white text-xs font-bold px-3 py-1.5 rounded-lg cursor-pointer flex items-center gap-1 hover:bg-amber-900 shadow-md">
                    <RefreshCw className="w-3.5 h-3.5" /> Change Photo
                    <input type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
                  </label>
                </div>
              )}
            </div>

            {/* Step 2: Voice Note */}
            <div className="space-y-3">
              <label className="block text-sm font-extrabold text-amber-950 flex items-center gap-2">
                <span className="w-6 h-6 rounded-full bg-amber-600 text-white flex items-center justify-center text-xs font-bold">2</span>
                {t.voiceStep}
              </label>
              <AudioRecorder onAudioReady={(blob) => setAudioBlob(blob)} />
            </div>

            {/* Action Buttons */}
            <div className="flex items-center justify-between pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={onCancel}
                className="px-5 py-3 text-slate-600 font-bold text-sm hover:text-slate-900"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={loading || !imageFile}
                onClick={handleStartPipeline}
                className="px-8 py-4 bg-gradient-to-r from-amber-600 to-amber-700 hover:from-amber-500 hover:to-amber-600 text-white font-extrabold rounded-2xl shadow-lg transition-all flex items-center gap-2 text-base disabled:opacity-50"
              >
                <span>{loading ? 'Uploading...' : 'Generate AI Catalogue'}</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* STEP 2: AI Pipeline Polling Progress */}
        {step === 'processing' && (
          <div className="text-center py-12 space-y-6">
            <div className="relative inline-flex items-center justify-center w-24 h-24 rounded-full bg-amber-100 text-amber-600">
              <Sparkles className="w-12 h-12 animate-bounce" />
            </div>
            <div className="space-y-2">
              <h2 className="text-2xl font-extrabold text-amber-950">AI Orchestration Pipeline Running</h2>
              <p className="text-xs text-slate-500">Processing vision, speech transcription, pricing matrix & recommendations...</p>
            </div>

            {/* Progress bar */}
            <div className="max-w-md mx-auto space-y-2">
              <div className="h-4 w-full bg-amber-100 rounded-full overflow-hidden p-0.5 border border-amber-300">
                <div
                  className="h-full bg-gradient-to-r from-amber-500 to-amber-600 rounded-full transition-all duration-500"
                  style={{ width: `${processingStatus?.progress_percent || 25}%` }}
                />
              </div>
              <div className="flex justify-between text-xs font-bold text-amber-800">
                <span className="capitalize">{processingStatus?.step?.replace('_', ' ') || 'initializing'}</span>
                <span>{processingStatus?.progress_percent || 25}%</span>
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: Complete Results & Summary */}
        {step === 'done' && completedProduct && (
          <div className="space-y-6">
            <div className="bg-emerald-50 border-2 border-emerald-300 p-4 rounded-2xl flex items-center gap-3">
              <CheckCircle2 className="w-8 h-8 text-emerald-600 shrink-0" />
              <div>
                <h3 className="font-extrabold text-emerald-900 text-base">AI Cataloguing Complete!</h3>
                <p className="text-xs text-emerald-700">Product successfully catalogued & ready for buyers.</p>
              </div>
            </div>

            {/* Catalogue Details */}
            <div className="bg-amber-50/60 p-6 rounded-2xl border border-amber-200 space-y-4">
              <h3 className="text-lg font-extrabold text-amber-950">{completedProduct.catalogue?.name}</h3>
              <p className="text-xs text-slate-700 leading-relaxed">{completedProduct.catalogue?.description}</p>
              
              <div className="flex flex-wrap gap-2 pt-2">
                <span className="px-3 py-1 bg-amber-200 text-amber-900 font-bold text-xs rounded-full">
                  Craft: {completedProduct.catalogue?.craft}
                </span>
                <span className="px-3 py-1 bg-amber-200 text-amber-900 font-bold text-xs rounded-full">
                  Material: {completedProduct.catalogue?.material}
                </span>
              </div>
            </div>

            {/* Pricing Explanation Card */}
            <div className="bg-white p-6 rounded-2xl border-2 border-amber-400 shadow-sm space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-xs font-extrabold text-slate-500 uppercase tracking-wider">{t.suggestedPrice}</span>
                <div className="flex items-center text-2xl font-black text-amber-900">
                  <IndianRupee className="w-6 h-6 text-amber-600" />
                  <span>
                    {completedProduct.price?.suggested_price.toLocaleString('en-IN') ||
                     completedProduct.pricing?.suggested_price.toLocaleString('en-IN')}
                  </span>
                </div>
              </div>

              <p className="text-xs text-slate-600 bg-amber-50 p-3 rounded-xl border border-amber-200 italic">
                "{completedProduct.price?.explanation || completedProduct.pricing?.explanation}"
              </p>
            </div>

            {/* Action Buttons */}
            <button
              onClick={() => onComplete(completedProduct.product_id || completedProduct.id || '')}
              className="w-full py-4 bg-amber-600 hover:bg-amber-500 text-white font-extrabold rounded-2xl shadow-lg transition-all flex items-center justify-center gap-2 text-base"
            >
              <span>View Full Product & Buyer Opportunities</span>
              <ArrowRight className="w-5 h-5" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
