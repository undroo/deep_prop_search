import { PropertyData } from '../types/property';
import Image from 'next/image';

interface PropertyDisplayProps {
  property: PropertyData;
}

export default function PropertyDisplay({ property }: PropertyDisplayProps) {
  console.log('Property data received:', property);

  return (
    <div className="max-w-4xl mx-auto p-6 bg-white rounded-lg shadow-lg">
      {/* Property Images */}
      <div className="relative h-[400px] mb-6">
        {property.images.length > 0 && (
          <Image
            src={property.images[0]}
            alt={`${property.address.full_address}`}
            fill
            className="object-cover rounded-lg"
          />
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

        <div className="pt-4 border-t">
          <h2 className="text-xl font-semibold mb-2">Description</h2>
          <p className="text-gray-600 whitespace-pre-line">
            {property.description}
          </p>
        </div>
      </div>
    </div>
  );
} 