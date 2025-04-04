import { AnalysisData, PropertyData, DistanceInfo } from '../types/property';

export interface ChatMessage {
    content: string;
    timestamp: string;
    agent?: string;
    analysis?: AnalysisData;
}

export interface AnalysisRequestBody {
    property_data: PropertyData;
    distance_info: DistanceInfo;
    agent: string;
    chat_history?: ChatMessage[];
    current_question?: string;
}

export interface AnalysisResponse {
    analysis: AnalysisData;
    timestamp: string;
    agent: string;
}

export interface ChatAnalysisProps {
    property: PropertyData;
    distanceInfo?: DistanceInfo;
}