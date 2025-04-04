import React from 'react';
import { PropertyData, DistanceInfo } from '../types/property';
import DistanceInfoDisplay from './DistanceInfoDisplay';

interface PropertyDetailsProps {
    property: PropertyData;
    distanceInfo?: DistanceInfo;
}

const PropertyDetails: React.FC<PropertyDetailsProps> = ({ property, distanceInfo }) => {
    return (
        <div className="space-y-6">
            {/* Existing property details */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-2xl font-bold mb-4">{property.address.full_address}</h2>
                <div className="grid grid-cols-2 gap-4 mb-4">
                    <div>
                        <p className="text-sm text-gray-600">Price</p>
                        <p className="text-xl font-semibold">${property.basic_info.price}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-600">Property Type</p>
                        <p className="text-xl font-semibold">{property.basic_info.property_type}</p>
                    </div>
                </div>
                <div className="grid grid-cols-4 gap-4">
                    <div>
                        <p className="text-sm text-gray-600">Bedrooms</p>
                        <p className="text-lg font-medium">{property.features.bedrooms}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-600">Bathrooms</p>
                        <p className="text-lg font-medium">{property.features.bathrooms}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-600">Parking</p>
                        <p className="text-lg font-medium">{property.features.parking}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-600">Land Size</p>
                        <p className="text-lg font-medium">{property.features.land_size}m²</p>
                    </div>
                </div>
            </div>

            {/* Description */}
            <div className="bg-white rounded-lg shadow p-6">
                <h2 className="text-xl font-bold mb-4">Description</h2>
                <p className="text-gray-700 whitespace-pre-line">{property.description}</p>
            </div>

            {/* Distance Information */}
            {distanceInfo && (
                <div className="bg-white rounded-lg shadow p-6">
                    <h2 className="text-xl font-bold mb-4">Location Information</h2>
                    <DistanceInfoDisplay />
                </div>
            )}
        </div>
    );
};

export default PropertyDetails; 