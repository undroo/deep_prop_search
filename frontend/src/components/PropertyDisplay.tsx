import { PropertyData } from '../types/property';
import Image from 'next/image';
import { useState } from 'react';

interface PropertyDisplayProps {
  property: PropertyData;
}

export default function PropertyDisplay({ property }: PropertyDisplayProps) {
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(true);
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);

  const toggleDescription = () => {
    setIsDescriptionExpanded(!isDescriptionExpanded);
  };

  const nextImage = () => {
    setSelectedImageIndex((prev) => (prev + 1) % property.images.length);
  };

  const previousImage = () => {
    setSelectedImageIndex((prev) => (prev - 1 + property.images.length) % property.images.length);
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* Image Gallery */}
      <div className="relative h-[400px] mb-6">
        {property.images.length > 0 && (
          <>
            <Image
              src={property.images[selectedImageIndex]}
              alt={`${property.address.full_address}`}
              fill
              className="object-cover rounded-lg"
            />
            {property.images.length > 1 && (
              <>
                <button
                  onClick={previousImage}
                  className="absolute left-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75"
                >
                  ←
                </button>
                <button
                  onClick={nextImage}
                  className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75"
                >
                  →
                </button>
                <div className="absolute bottom-2 left-1/2 transform -translate-x-1/2 flex space-x-2">
                  {property.images.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setSelectedImageIndex(index)}
                      className={`w-2 h-2 rounded-full ${
                        index === selectedImageIndex ? 'bg-white' : 'bg-white/50'
                      }`}
                    />
                  ))}
                </div>
              </>
            )}
          </>
        )}
      </div>

      {/* Property Details */}
      <div className="space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">
          {property.address.full_address}
        </h1>
        
        <p className="text-2xl font-semibold text-blue-600">
          {property.basic_info.price}
        </p>

        <div className="flex space-x-6 text-gray-600">
          {property.features.bedrooms !== undefined && (
            <div>
              <span className="font-medium">{property.features.bedrooms}</span> beds
            </div>
          )}
          {property.features.bathrooms !== undefined && (
            <div>
              <span className="font-medium">{property.features.bathrooms}</span> baths
            </div>
          )}
          {property.features.parking !== undefined && (
            <div>
              <span className="font-medium">{property.features.parking}</span> parking
            </div>
          )}
          {property.basic_info.property_type && (
            <div>
              <span className="font-medium">{property.basic_info.property_type}</span>
            </div>
          )}
        </div>

        {/* Collapsible Description */}
        <div className="pt-4 border-t">
          <button
            onClick={toggleDescription}
            className="flex items-center justify-between w-full text-left"
          >
            <h2 className="text-xl font-semibold">Description</h2>
            <span className="text-gray-500">
              {isDescriptionExpanded ? '▼' : '▶'}
            </span>
          </button>
          {isDescriptionExpanded && (
            <p className="mt-2 text-gray-600 whitespace-pre-line">
              {property.description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
} 