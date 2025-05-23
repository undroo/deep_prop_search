'use client';

import { useState } from 'react';
import PropertyForm from './PropertyForm';
import PropertyDisplay from './PropertyDisplay';
import ChatAnalysis from './ChatAnalysis';
import DistanceInfoDisplay from './DistanceInfoDisplay';
import { PropertyFormData } from '../types/property';
import { initializeProperty } from '../utils/api';
import { useTabs } from '../context/TabsContext';

export default function Home() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const {
    propertyData,
    setPropertyData,
    distanceInfo,
    setDistanceInfo,
    activeTab,
    setActiveTab
  } = useTabs();

  const handleSubmit = async (data: PropertyFormData) => {
    setIsLoading(true);
    setError(null);
    setPropertyData(null);
    setDistanceInfo(null);

    try {
      const result = await initializeProperty(data);

      if (result.status === 'error') {
        setError(result.error || 'An error occurred while analyzing the property');
      } else if (result.property_data) {
        setPropertyData(result.property_data);
        setDistanceInfo(result.distance_info || null);
      }
    } catch (err) {
      console.error('Error:', err);
      setError('Failed to connect to the server. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Property Analysis
          </h1>
          <p className="text-lg text-gray-700">
            Enter a Domain.com.au property URL to analyze
          </p>
        </div>

        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <PropertyForm onSubmit={handleSubmit} isLoading={isLoading} />
        </div>

        {error && (
          <div className="mb-8 p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-600">{error}</p>
          </div>
        )}

        {propertyData && (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Tab Navigation */}
            <div className="border-b border-gray-200">
              <nav className="flex">
                <button
                  onClick={() => setActiveTab('property')}
                  className={`px-6 py-4 text-sm font-medium ${
                    activeTab === 'property'
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Property Details
                </button>
                <button
                  onClick={() => setActiveTab('distance')}
                  className={`px-6 py-4 text-sm font-medium ${
                    activeTab === 'distance'
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Location Information
                </button>
                <button
                  onClick={() => setActiveTab('chat')}
                  className={`px-6 py-4 text-sm font-medium ${
                    activeTab === 'chat'
                      ? 'text-blue-600 border-b-2 border-blue-600'
                      : 'text-gray-500 hover:text-gray-700'
                  }`}
                >
                  Chat Analysis
                </button>
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {activeTab === 'property' && (
                <PropertyDisplay />
              )}
              {activeTab === 'distance' && distanceInfo && (
                <div className="max-w-4xl mx-auto">
                  <DistanceInfoDisplay />
                </div>
              )}
              {activeTab === 'chat' && (
                <ChatAnalysis />
              )}
            </div>
          </div>
        )}
      </div>
    </main>
  );
} 