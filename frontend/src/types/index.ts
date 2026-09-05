export type UserRole = 'ARTISAN' | 'ADMIN' | 'BUYER';

export interface User {
  user_id: string;
  name: string;
  role: UserRole;
  phone: string;
}

export interface AuthResponseData {
  user_id: string;
  name: string;
  role: UserRole;
  token: string;
}

export interface ProductCreateResponse {
  product_id: string;
  status: string;
}

export interface UploadImageResponse {
  product_id: string;
  image_url: string;
}

export interface UploadAudioResponse {
  product_id: string;
  audio_url: string;
}

export interface ProcessProductResponse {
  product_id: string;
  status: string;
  job_id: string;
}

export interface Catalogue {
  id?: string;
  product_id?: string;
  name: string;
  category: string;
  material: string;
  craft: string;
  description: string;
  tags: string[];
}

export interface Price {
  suggested_price: number;
  price_range: [number, number];
  explanation: string;
}

export interface Opportunity {
  buyer_name: string;
  match_score: number;
  location: string;
  requirement: string;
}

export interface OpportunityListItem {
  opportunity_id: string;
  product_id: string;
  buyer_name: string;
  company_name: string;
  match_score: number;
  status: string;
  requirement: string;
}

export interface ProductImage {
  id: string;
  url: string;
}

export interface ProductAudio {
  id: string;
  url: string;
}

export interface ProductDetail {
  product_id: string;
  id?: string;
  artisan_id: string;
  status: 'DRAFT' | 'PROCESSING' | 'READY' | 'PUBLISHED' | 'FAILED';
  created_at: string;
  image_url?: string;
  images: ProductImage[];
  audio: ProductAudio[];
  catalogue?: Catalogue;
  price?: Price;
  pricing?: {
    id: string;
    suggested_price: number;
    price_range_low: number;
    price_range_high: number;
    explanation: string;
  };
  opportunities: Opportunity[];
}

export interface ProcessingStatusData {
  product_id: string;
  status: 'DRAFT' | 'PROCESSING' | 'READY' | 'PUBLISHED' | 'FAILED';
  step: string;
  progress_percent: number;
}

export interface CatalogueStatusCounts {
  ready: number;
  processing: number;
  draft: number;
}

export interface DashboardSummary {
  total_products: number;
  catalogue_status: CatalogueStatusCounts;
  recent_products: ProductDetail[];
}

export interface InsightItem {
  type: string;
  message: string;
}

export interface ApiResponseEnvelope<T> {
  success: boolean;
  data: T | null;
  error: {
    code: string;
    message: string;
  } | null;
}
