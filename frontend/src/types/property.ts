export interface PropertyAddress {
  full_address: string;
}

export interface PropertyBasicInfo {
  price: number;
  property_type: string;
  title: string;
  url: string;
}

export interface PropertyFeatures {
  bedrooms: number;
  bathrooms: number;
  parking: number;
  land_size: number;
  property_size: number;
}

export interface PropertyData {
  address: PropertyAddress;
  basic_info: PropertyBasicInfo;
  features: PropertyFeatures;
  images: string[];
  description: string;
}

export interface PropertyResponse {
  session_id: string;
  status: 'ready' | 'error';
  property_data?: PropertyData;
  distance_info?: any; // We'll type this later when we implement maps
  error?: string;
}

export interface PropertyFormData {
  url: string;
  categories?: string[];
} 