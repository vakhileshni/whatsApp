'use client';

import { useEffect, useState } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';

interface Restaurant {
  id: string;
  name: string;
  address: string;
  distance: number;
  delivery_fee: number;
  cuisine_type: string;
  serial: number;
  rating?: number;
  customer_rating?: number;
  total_orders?: number;
  has_discount?: boolean;
  max_discount_percentage?: number;
}

export default function RestaurantsPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const lat = parseFloat(searchParams.get('lat') || '0');
  const lon = parseFloat(searchParams.get('lon') || '0');
  const token = searchParams.get('token');
  const customerName = searchParams.get('name') || 'Customer';

  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [allRestaurants, setAllRestaurants] = useState<Restaurant[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [maxDistance, setMaxDistance] = useState(3);
  const [selectedCuisines, setSelectedCuisines] = useState<string[]>(['all']);
  const [showFilters, setShowFilters] = useState(false);
  const [locationName, setLocationName] = useState<string>('');

  useEffect(() => {
    if (lat && lon) {
      fetchRestaurants();
      fetchLocationName(lat, lon);
    } else {
      setError('Location not provided. Please share your location again.');
      setLoading(false);
    }
  }, [lat, lon, maxDistance]);
  
  const fetchLocationName = async (latitude: number, longitude: number) => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10&addressdetails=1`,
        {
          headers: {
            'User-Agent': 'WhatsAppOrderingApp/1.0'
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        if (data.address) {
          const addr = data.address;
          const locationName = addr.city || addr.town || addr.village || addr.suburb || 
                             addr.neighbourhood || addr.county || addr.state || 
                             `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
          setLocationName(locationName);
        } else {
          setLocationName(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
        }
      } else {
        setLocationName(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
      }
    } catch (error) {
      console.error('Error fetching location name:', error);
      setLocationName(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
    }
  };

  useEffect(() => {
    if (allRestaurants.length === 0) return;
    
    if (selectedCuisines.includes('all') || selectedCuisines.length === 0) {
      setRestaurants(allRestaurants);
      return;
    }
    
    const filtered = allRestaurants.filter((restaurant) => {
      const cuisine = restaurant.cuisine_type.toLowerCase();
      return selectedCuisines.some((selected) => {
        if (selected === 'veg') {
          return cuisine === 'veg' || cuisine === 'both' || cuisine === 'full-meal';
        } else if (selected === 'non-veg') {
          return cuisine === 'non-veg' || cuisine === 'both' || cuisine === 'full-meal';
        } else {
          return cuisine === selected || cuisine === 'both';
        }
      });
    });
    
    setRestaurants(filtered);
  }, [selectedCuisines, allRestaurants]);

  const fetchRestaurants = async () => {
    try {
      setLoading(true);
      setError('');
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';
      const url = `${API_BASE_URL}/api/public/restaurants?latitude=${lat}&longitude=${lon}&max_distance=${maxDistance}`;
      
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
      });
      
      if (!response.ok) {
        throw new Error(`Failed to fetch restaurants: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      const fetchedRestaurants = data.restaurants || [];
      setAllRestaurants(fetchedRestaurants);
      setRestaurants(fetchedRestaurants);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load restaurants';
      setError(errorMessage);
      console.error('❌ Error fetching restaurants:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSelectRestaurant = (restaurantId: string) => {
    const menuUrl = `/menu/${restaurantId}?token=${encodeURIComponent(token || '')}&lat=${lat}&lon=${lon}&name=${encodeURIComponent(customerName)}`;
    router.push(menuUrl);
  };

  const toggleCuisine = (value: string) => {
    if (value === 'all') {
      setSelectedCuisines(['all']);
    } else {
      setSelectedCuisines((prev) => {
        const withoutAll = prev.filter((c) => c !== 'all');
        
        if (withoutAll.includes(value)) {
          const newSelection = withoutAll.filter((c) => c !== value);
          return newSelection.length === 0 ? ['all'] : newSelection;
        } else {
          return [...withoutAll, value];
        }
      });
    }
  };

  const cuisineOptions = [
    { value: 'all', label: 'All Cuisines', emoji: '🍽️', color: 'from-purple-500 to-indigo-500' },
    { value: 'veg', label: 'Veg', emoji: '🟢', color: 'from-green-500 to-emerald-500' },
    { value: 'non-veg', label: 'Non-Veg', emoji: '🔴', color: 'from-red-500 to-rose-500' },
    { value: 'snack', label: 'Snack', emoji: '🍟', color: 'from-orange-500 to-amber-500' },
    { value: 'full-meal', label: 'Full Meal', emoji: '🍽️', color: 'from-blue-500 to-cyan-500' },
  ];

  const distanceOptions = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 via-indigo-600 to-pink-500">
        <div className="text-center">
          <div className="relative w-20 h-20 mx-auto mb-4">
            <div className="absolute inset-0 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
          </div>
          <div className="text-white text-xl font-semibold">Discovering amazing restaurants...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 via-indigo-600 to-pink-500 p-4">
        <div className="text-center bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-md">
          <div className="text-white text-xl mb-4 font-semibold">{error}</div>
          <button
            onClick={() => fetchRestaurants()}
            className="mt-4 bg-white text-purple-600 px-8 py-3 rounded-xl font-bold hover:bg-purple-50 transition-all transform hover:scale-105 shadow-lg"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/30 to-indigo-50/30">
      {/* Enhanced Header with Glassmorphism */}
      <div className="bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-700 text-white shadow-xl relative overflow-hidden">
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}></div>
        <div className="relative p-4 sm:p-5 text-center">
          <h1 className="text-lg sm:text-xl md:text-2xl font-bold drop-shadow-lg">
            👋 Welcome, {customerName}
          </h1>
          <p className="text-sm sm:text-base text-purple-100 mt-1 flex items-center justify-center gap-1">
            <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
            </svg>
            {locationName || `${lat.toFixed(4)}, ${lon.toFixed(4)}`}
          </p>
        </div>
      </div>

      {/* Enhanced Filters Section */}
      <div className="bg-white/80 backdrop-blur-sm shadow-lg sticky top-0 z-20 border-b border-purple-100">
        <div className="max-w-7xl mx-auto p-4 sm:p-5">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="w-full bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 py-3.5 px-4 rounded-2xl font-bold flex items-center justify-between hover:from-purple-200 hover:to-indigo-200 transition-all duration-300 shadow-md hover:shadow-xl transform hover:scale-[1.01] text-sm sm:text-base"
          >
            <span className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
              </svg>
              Filters {selectedCuisines.length > 0 && selectedCuisines[0] !== 'all' && (
                <span className="bg-purple-600 text-white px-2 py-0.5 rounded-full text-xs">
                  {selectedCuisines.length}
                </span>
              )}
            </span>
            <svg className={`w-5 h-5 transition-transform duration-300 ${showFilters ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {showFilters && (
            <div className="mt-5 space-y-6 animate-fadeIn">
              {/* Distance Filter */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                  Maximum Distance: <span className="text-purple-600">{maxDistance} km</span>
                </label>
                <div className="flex flex-wrap gap-2">
                  {distanceOptions.map((distance) => (
                    <button
                      key={distance}
                      onClick={() => setMaxDistance(distance)}
                      className={`px-4 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 transform hover:scale-105 ${
                        maxDistance === distance
                          ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white shadow-lg scale-105'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200 shadow-md hover:shadow-lg'
                      }`}
                    >
                      {distance} km
                    </button>
                  ))}
                </div>
              </div>

              {/* Cuisine Type Filter */}
              <div>
                <label className="block text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                  </svg>
                  Cuisine Type (Select Multiple)
                </label>
                <div className="flex flex-wrap gap-2.5">
                  {cuisineOptions.map((option) => {
                    const isSelected = selectedCuisines.includes(option.value);
                    return (
                      <button
                        key={option.value}
                        onClick={() => toggleCuisine(option.value)}
                        className={`px-4 py-2.5 rounded-xl font-bold text-sm transition-all duration-300 transform hover:scale-105 flex items-center gap-2 shadow-md ${
                          isSelected
                            ? `bg-gradient-to-r ${option.color} text-white shadow-xl scale-105`
                            : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200 hover:border-gray-300'
                        }`}
                      >
                        <span className="text-lg">{option.emoji}</span>
                        <span>{option.label}</span>
                        {isSelected && (
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                          </svg>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Results Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        <div className="flex items-center justify-between mb-6">
          <div className="text-gray-700 font-semibold text-base sm:text-lg">
            <span className="text-purple-600 font-bold">{restaurants.length}</span> {restaurants.length !== 1 ? 'restaurants' : 'restaurant'} found
            {selectedCuisines.length > 0 && selectedCuisines[0] !== 'all' && (
              <span className="ml-2 text-gray-500 text-sm">
                ({selectedCuisines.map((c) => cuisineOptions.find((o) => o.value === c)?.label).join(', ')})
              </span>
            )}
            <span className="ml-2 text-gray-500">within {maxDistance} km</span>
          </div>
        </div>

        {/* Restaurant Grid */}
        {restaurants.length === 0 ? (
          <div className="bg-white rounded-3xl shadow-xl p-12 text-center border border-gray-100">
            <div className="text-6xl mb-4">😔</div>
            <div className="text-gray-700 text-xl font-bold mb-2">No restaurants found</div>
            <p className="text-gray-500">
              Try adjusting your filters or increasing the distance range.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-5">
            {restaurants.map((restaurant, index) => (
              <div
                key={restaurant.id}
                onClick={() => handleSelectRestaurant(restaurant.id)}
                className={`group bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 cursor-pointer border-2 overflow-hidden transform hover:-translate-y-2 ${
                  restaurant.has_discount 
                    ? 'border-green-400 hover:border-green-500 bg-gradient-to-br from-green-50/50 to-white' 
                    : 'border-transparent hover:border-purple-300'
                } relative`}
              >
                {/* Discount Badge */}
                {restaurant.has_discount && restaurant.max_discount_percentage && (
                  <div className="absolute top-2 right-2 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg z-10 animate-pulse">
                    🎉 Up to {restaurant.max_discount_percentage}% OFF
                  </div>
                )}

                <div className="p-4 sm:p-5">
                  {/* Restaurant Number & Name */}
                  <div className="mb-3">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="bg-gradient-to-r from-purple-100 to-indigo-100 text-purple-700 text-xs font-bold px-2 py-1 rounded-lg">
                        #{index + 1}
                      </span>
                      <h2 className={`text-base sm:text-lg font-bold line-clamp-1 flex-1 ${
                        restaurant.has_discount ? 'text-green-700' : 'text-gray-800'
                      }`}>
                        {restaurant.name}
                      </h2>
                    </div>
                    <p className="text-gray-600 text-xs sm:text-sm line-clamp-2 min-h-[2.5rem] flex items-start gap-1">
                      <svg className="w-4 h-4 text-gray-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      {restaurant.address}
                    </p>
                  </div>

                  {/* Stats */}
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center flex-wrap gap-2 text-xs">
                      <span className="bg-purple-100 text-purple-700 px-2.5 py-1 rounded-lg font-semibold flex items-center gap-1">
                        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                        </svg>
                        {restaurant.distance} km
                      </span>
                      <span className="bg-gray-100 text-gray-700 px-2.5 py-1 rounded-lg font-semibold">
                        🚚 ₹{restaurant.delivery_fee}
                      </span>
                      {restaurant.rating && (
                        <span className="bg-yellow-100 text-yellow-700 px-2.5 py-1 rounded-lg font-bold flex items-center gap-1">
                          ⭐ {restaurant.rating.toFixed(1)}
                          {restaurant.total_orders && restaurant.total_orders > 0 && (
                            <span className="text-yellow-600 text-xs">({restaurant.total_orders})</span>
                          )}
                        </span>
                      )}
                    </div>
                    <span className={`inline-block px-3 py-1 rounded-lg text-xs font-bold ${
                      restaurant.cuisine_type === 'veg' ? 'bg-green-100 text-green-700' :
                      restaurant.cuisine_type === 'non-veg' ? 'bg-red-100 text-red-700' :
                      restaurant.cuisine_type === 'both' ? 'bg-yellow-100 text-yellow-700' :
                      restaurant.cuisine_type === 'snack' ? 'bg-orange-100 text-orange-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {restaurant.cuisine_type === 'veg' && '🟢 Veg'}
                      {restaurant.cuisine_type === 'non-veg' && '🔴 Non-Veg'}
                      {restaurant.cuisine_type === 'both' && '🟡 Both'}
                      {restaurant.cuisine_type === 'snack' && '🍟 Snack'}
                      {restaurant.cuisine_type === 'full-meal' && '🍽️ Full Meal'}
                    </span>
                  </div>

                  {/* CTA Button */}
                  <button className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white px-4 py-3 rounded-xl font-bold hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl transform group-hover:scale-105 text-sm flex items-center justify-center gap-2">
                    <span>View Menu</span>
                    <svg className="w-4 h-4 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <style jsx>{`
        @keyframes fadeIn {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
      `}</style>
    </div>
  );
}