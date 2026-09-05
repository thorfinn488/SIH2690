import React, { createContext, useContext, useState } from 'react';

type Language = 'en' | 'hi';

interface Translations {
  appName: string;
  tagline: string;
  login: string;
  register: string;
  logout: string;
  phone: string;
  password: string;
  name: string;
  role: string;
  artisan: string;
  buyer: string;
  admin: string;
  dashboard: string;
  products: string;
  addProduct: string;
  opportunities: string;
  insights: string;
  totalProducts: string;
  readyCatalogues: string;
  processing: string;
  drafts: string;
  photoStep: string;
  voiceStep: string;
  processStep: string;
  suggestedPrice: string;
  priceRange: string;
  fairExplanation: string;
  craftStory: string;
  matchingBuyers: string;
  quickDemo: string;
  micRecording: string;
  tapToRecord: string;
  recordingActive: string;
}

const translations: Record<Language, Translations> = {
  en: {
    appName: 'KalaSaathi',
    tagline: 'AI Business Manager for Artisans',
    login: 'Log In',
    register: 'Sign Up',
    logout: 'Log Out',
    phone: 'Phone Number',
    password: 'Password',
    name: 'Full Name',
    role: 'Role',
    artisan: 'Artisan (दस्तकार)',
    buyer: 'Buyer (खरीदार)',
    admin: 'Admin',
    dashboard: 'Dashboard',
    products: 'My Products',
    addProduct: 'Add New Product',
    opportunities: 'Buyer Opportunities',
    insights: 'Market Insights',
    totalProducts: 'Total Products',
    readyCatalogues: 'Ready Catalogues',
    processing: 'In Processing',
    drafts: 'Drafts',
    photoStep: 'Take / Upload Photo',
    voiceStep: 'Speak About Product',
    processStep: 'AI Cataloging & Pricing',
    suggestedPrice: 'Suggested Fair Price',
    priceRange: 'Recommended Price Range',
    fairExplanation: 'Why this price is fair',
    craftStory: 'Artisan Craft Description',
    matchingBuyers: 'Interested Buyers',
    quickDemo: 'Quick Demo Accounts',
    micRecording: 'Voice Description',
    tapToRecord: 'Tap microphone to speak about your craft',
    recordingActive: 'Recording... Speak now',
  },
  hi: {
    appName: 'कलासाथी',
    tagline: 'कारीगरों के लिए AI व्यापार प्रबन्धक',
    login: 'लॉग इन करें',
    register: 'नया खाता बनाएं',
    logout: 'लॉग आउट',
    phone: 'फोन नंबर',
    password: 'पासवर्ड',
    name: 'पूरा नाम',
    role: 'भूमिका',
    artisan: 'कारीगर / दस्तकार',
    buyer: 'खरीदार / व्यापारी',
    admin: 'एडमिन',
    dashboard: 'डैशबोर्ड',
    products: 'मेरे उत्पाद',
    addProduct: '+ नया उत्पाद जोड़ें',
    opportunities: 'खरीदार अवसर',
    insights: 'बाज़ार अंतर्दृष्टि',
    totalProducts: 'कुल उत्पाद',
    readyCatalogues: 'तैयार कैटलॉग',
    processing: 'प्रसंस्करण में',
    drafts: 'ड्राफ्ट',
    photoStep: 'उत्पाद की फोटो लें',
    voiceStep: 'उत्पाद के बारे में बोलें',
    processStep: 'AI कैटलॉग और मूल्य निर्धारण',
    suggestedPrice: 'अनुशंसित उचित मूल्य',
    priceRange: 'मूल्य सीमा (बाज़ार दर)',
    fairExplanation: 'यह कीमत उचित क्यों है',
    craftStory: 'शिल्प कला का विवरण',
    matchingBuyers: 'इच्छुक खरीदार',
    quickDemo: 'त्वरित डेमो खाते',
    micRecording: 'आवाज़ से विवरण दें',
    tapToRecord: 'अपने उत्पाद के बारे में बोलने के लिए माइक दबाएं',
    recordingActive: 'रिकॉर्डिंग चालू है... अब बोलें',
  },
};

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: Translations;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [language, setLanguage] = useState<Language>('en');

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t: translations[language] }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) throw new Error('useLanguage must be used within LanguageProvider');
  return context;
};
