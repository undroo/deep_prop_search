import { PropertyFormData, PropertyResponse } from '../types/property';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export async function initializeProperty(data: PropertyFormData): Promise<PropertyResponse> {
  try {
    console.log('Sending request to:', `${API_BASE_URL}/initialize`);
    console.log('Request data:', data);

    const response = await fetch(`${API_BASE_URL}/initialize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify(data),
    });

    console.log('Response status:', response.status);
    console.log('Response headers:', Object.fromEntries(response.headers.entries()));

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Error response body:', errorText);
      throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
    }

    const result = await response.json();
    console.log('Response data:', result);
    return result;
  } catch (error) {
    console.error('API Error:', error);
    if (error instanceof Error) {
      console.error('Error message:', error.message);
      console.error('Error stack:', error.stack);
    }
    throw error;
  }
} 