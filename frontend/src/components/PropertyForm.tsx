import { useState } from 'react';
import { PropertyFormData } from '../types/property';

interface PropertyFormProps {
  onSubmit: (data: PropertyFormData) => Promise<void>;
  isLoading: boolean;
}

export default function PropertyForm({ onSubmit, isLoading }: PropertyFormProps) {
  const [url, setUrl] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit({ url });
  };

  return (
    <form onSubmit={handleSubmit} className="w-full max-w-2xl mx-auto">
      <div className="flex flex-col space-y-4">
        <div>
          <label htmlFor="url" className="block text-sm font-medium text-gray-700">
            Domain.com.au Property URL
          </label>
          <div className="mt-1">
            <input
              type="url"
              id="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://www.domain.com.au/..."
              className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm"
              required
            />
          </div>
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isLoading ? 'Loading...' : 'Analyze Property'}
        </button>
      </div>
    </form>
  );
} 