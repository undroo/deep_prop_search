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

export interface TravelTime {
    text: string;
    value: number;
}

export interface TravelModes {
    driving?: {
        current?: TravelTime;
        morning_peak?: TravelTime;
        evening_peak?: TravelTime;
    };
    transit?: {
        current?: TravelTime;
        morning_peak?: TravelTime;
        evening_peak?: TravelTime;
    };
    walking?: {
        current?: TravelTime;
    };
}

export interface LocationDistance {
    destination: string;
    distance: {
        text: string;
        value: number;
    };
    modes: TravelModes;
}

export interface DistanceInfo {
    work?: LocationDistance[];
    groceries?: LocationDistance[];
    schools?: LocationDistance[];
}

export interface AnalysisData {
  overview: {
    property_type: string;
    key_features: string[];
    condition: string;
    unique_selling_points: string[];
  };
  strengths: {
    physical_attributes: string[];
    location_advantages: string[];
    investment_potential: string[];
    lifestyle_benefits: string[];
  };
  concerns: {
    physical_issues: string[];
    location_disadvantages: string[];
    investment_risks: string[];
    lifestyle_limitations: string[];
  };
  investment_analysis: {
    price_assessment: string;
    market_position: string;
    growth_potential: string;
    rental_potential: string;
    holding_costs: string[];
  };
  recommendation: {
    summary: string;
    suitable_buyer_types: string[];
    key_considerations: string[];
    next_steps: string[];
  };
  property_analysis: {
    build_quality: string;
    layout: string;
    features: string;
    storage: string;
    lighting: string;
    renovation: string;
  };
  location_assessment: {
    neighborhood: string;
    transport: string;
    amenities: string;
    development: string;
    noise: string;
  };
  market_analysis: {
    position: string;
    comparables: string;
    recent_sales: string;
    trends: string;
    investment: string;
  };
  buyer_recommendations: {
    suitable_buyers: string[];
    negotiation_points: string[];
    additional_costs: string[];
    due_diligence: string[];
  };
  inspection_checklist: {
    key_areas: string[];
    red_flags: string[];
    agent_questions: string[];
    required_documents: string[];
  };
  risk_assessment: {
    structural: string[];
    legal: string[];
    financial: string[];
    environmental: string[];
    maintenance: string[];
  };
}