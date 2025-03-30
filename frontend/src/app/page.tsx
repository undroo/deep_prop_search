'use client';

import { useState } from 'react';
import PropertyForm from '../components/PropertyForm';
import PropertyDisplay from '../components/PropertyDisplay';
import { PropertyResponse, PropertyFormData } from '../types/property';
import { initializeProperty } from '../utils/api';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [propertyData, setPropertyData] = useState<PropertyResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: PropertyFormData) => {
    setIsLoading(true);
    setError(null);
    setPropertyData(null);

    try {
      const result = await initializeProperty(data);

      if (result.status === 'error') {
        setError(result.error || 'An error occurred while analyzing the property');
      } else {
        setPropertyData(result);
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Failed to connect to the server. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Property Analysis
          </h1>
          <p className="text-lg text-gray-600">
            Enter a Domain.com.au property URL to analyze
          </p>
        </div>

        <PropertyForm onSubmit={handleSubmit} isLoading={isLoading} />

        {error && (
          <div className="mt-8 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {propertyData?.property_data && (
          <div className="mt-12">
            <PropertyDisplay property={propertyData.property_data} />
          </div>
        )}
      </div>
    </main>
  );
}
