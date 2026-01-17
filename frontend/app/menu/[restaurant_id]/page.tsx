'use client';

import { useEffect, useState } from 'react';
import { useParams, useSearchParams, useRouter } from 'next/navigation';

interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  discounted_price?: number;
  discount_percentage?: number;
  is_available?: boolean;
}

interface Category {
  name: string;
  items: MenuItem[];
}

interface Restaurant {
  id: string;
  name: string;
  address: string;
  latitude?: number;
  longitude?: number;
  delivery_fee: number;
  upi_id: string;
  delivery_available?: boolean;
}

interface MenuData {
  restaurant: Restaurant;
  categories: Category[];
}

interface CartItem extends MenuItem {
  quantity: number;
}

export default function MenuPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const restaurantId = params.restaurant_id as string;
  const token = searchParams.get('token'); // phone number
  const lat = searchParams.get('lat');
  const lon = searchParams.get('lon');
  const customerNameFromWhatsApp = searchParams.get('name') || ''; // Customer name from WhatsApp
  
  // Function to go back to restaurant list
  const handleBackToRestaurants = () => {
    if (lat && lon && token) {
      router.push(`/restaurants?lat=${lat}&lon=${lon}&token=${encodeURIComponent(token)}`);
    } else {
      router.back();
    }
  };

  const [menuData, setMenuData] = useState<MenuData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [cart, setCart] = useState<CartItem[]>([]);
  const [showCheckout, setShowCheckout] = useState(false);
  const [customerName, setCustomerName] = useState(customerNameFromWhatsApp); // Auto-fill from WhatsApp
  const [orderType, setOrderType] = useState<'pickup' | 'delivery'>('delivery');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [alternatePhone, setAlternatePhone] = useState('');
  const [paymentMethod, setPaymentMethod] = useState<'cod' | 'online'>('cod');
  const [customerLat, setCustomerLat] = useState<number | null>(null);
  const [customerLon, setCustomerLon] = useState<number | null>(null);
  const [locationName, setLocationName] = useState<string>(''); // Location name (e.g., "Lucknow")
  const [showLocationModal, setShowLocationModal] = useState(false); // Show location modal
  const [distance, setDistance] = useState<number | null>(null); // Distance to restaurant in km
  const [showMapModal, setShowMapModal] = useState(false); // Show map modal
  const [showPickupConfirm, setShowPickupConfirm] = useState(false); // Show pickup location confirmation
  const [showLocationModal, setShowLocationModal] = useState(false); // Show location modal
  const [distance, setDistance] = useState<number | null>(null); // Distance to restaurant in km

  useEffect(() => {
    if (restaurantId) {
      fetchMenu();
    }
    
    // Get location from URL params
    const latParam = searchParams.get('lat');
    const lonParam = searchParams.get('lon');
    if (latParam && lonParam) {
      const lat = parseFloat(latParam);
      const lon = parseFloat(lonParam);
      if (!isNaN(lat) && !isNaN(lon)) {
        setCustomerLat(lat);
        setCustomerLon(lon);
        // Auto-fill delivery address from coordinates
        fetchAddressFromCoordinates(lat, lon);
        // Fetch location name
        fetchLocationName(lat, lon);
      }
    }
  }, [restaurantId, searchParams]);
  
  const fetchLocationName = async (latitude: number, longitude: number) => {
    try {
      // Use OpenStreetMap Nominatim API for reverse geocoding
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
          // Try to get city/town/village name
          const addr = data.address;
          const locName = addr.city || addr.town || addr.village || addr.suburb || 
                         addr.neighbourhood || addr.county || addr.state || 
                         `${latitude.toFixed(4)}, ${longitude.toFixed(4)}`;
          setLocationName(locName);
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
  
  // Auto-fill address when checkout opens and we have location
  useEffect(() => {
    if (showCheckout && customerLat && customerLon && !deliveryAddress) {
      fetchAddressFromCoordinates(customerLat, customerLon);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showCheckout, customerLat, customerLon, deliveryAddress]);
  
  const fetchAddressFromCoordinates = async (latitude: number, longitude: number) => {
    try {
      // Use OpenStreetMap Nominatim API for reverse geocoding (free, no API key needed)
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=18&addressdetails=1`,
        {
          headers: {
            'User-Agent': 'WhatsAppOrderingApp/1.0' // Required by Nominatim
          }
        }
      );
      
      if (response.ok) {
        const data = await response.json();
        if (data.address) {
          // Format address from OpenStreetMap data
          const addr = data.address;
          const addressParts = [
            addr.house_number,
            addr.road,
            addr.suburb || addr.neighbourhood,
            addr.city || addr.town || addr.village,
            addr.state,
            addr.postcode
          ].filter(Boolean);
          const formattedAddress = addressParts.join(', ');
          if (formattedAddress) {
            setDeliveryAddress(formattedAddress);
          } else {
            // Fallback: use coordinates
            setDeliveryAddress(`${latitude}, ${longitude}`);
          }
        } else {
          // Fallback: use coordinates
          setDeliveryAddress(`Location: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
        }
      } else {
        // Fallback: use coordinates
        setDeliveryAddress(`Location: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
      }
    } catch (error) {
      console.error('Error fetching address:', error);
      // Fallback: use coordinates
      setDeliveryAddress(`Location: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
    }
  };

  const fetchMenu = async () => {
    try {
      setLoading(true);
      setError('');
      // Direct fetch to avoid API client issues
      // This page is fully dynamic - it fetches menu for whatever restaurant_id is in the URL
      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';
      const apiUrl = `${API_BASE_URL}/api/public/menu/${restaurantId}`;
      
      console.log('🔍 Fetching menu for restaurant:', restaurantId);
      console.log('📡 API URL:', apiUrl);
      
      // First, test if backend is reachable
      try {
        const healthCheck = await fetch(`${API_BASE_URL}/health`, {
          method: 'GET',
          mode: 'cors',
        });
        console.log('🏥 Backend health check:', healthCheck.status);
      } catch (healthError) {
        console.warn('⚠️ Health check failed, but continuing...', healthError);
      }
      
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        mode: 'cors',
        cache: 'no-cache',
      });
      
      console.log('📥 Response status:', response.status);
      
      if (!response.ok) {
        let errorText = '';
        try {
          errorText = await response.text();
          console.error('❌ Error response:', errorText);
        } catch (e) {
          console.error('❌ Could not read error response');
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}${errorText ? ' - ' + errorText : ''}`);
      }
      
      const data = await response.json();
      console.log('✅ Menu data received:', data);
      
      if (!data || !data.restaurant || !data.categories) {
        throw new Error('Invalid menu data received from server');
      }
      
      setMenuData(data);
      
      // Calculate distance if we have customer and restaurant coordinates
      if (data.restaurant.latitude && data.restaurant.longitude && customerLat && customerLon) {
        const dist = calculateDistance(
          customerLat,
          customerLon,
          data.restaurant.latitude,
          data.restaurant.longitude
        );
        setDistance(dist);
      }
    } catch (err) {
      let errorMessage = 'Failed to load menu. Please try again.';
      const apiBase = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';
      
      if (err instanceof TypeError && err.message === 'Failed to fetch') {
        errorMessage = `Cannot connect to backend server.\n\nPlease ensure:\n1. Backend server is running on ${apiBase}\n2. Run: cd backend && uvicorn main:app --reload --port 4000\n3. Check if port 4000 is available\n4. Try opening ${apiBase}/health in your browser`;
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      console.error('❌ Menu fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Calculate distance between two coordinates (Haversine formula)
  const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a = 
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c; // Distance in km
  };

  // Get Google Maps link
  const getGoogleMapsLink = (): string => {
    if (menuData?.restaurant.latitude && menuData?.restaurant.longitude) {
      return `https://www.google.com/maps?q=${menuData.restaurant.latitude},${menuData.restaurant.longitude}`;
    } else if (menuData?.restaurant.address) {
      const encodedAddress = encodeURIComponent(menuData.restaurant.address);
      return `https://www.google.com/maps/search/?api=1&query=${encodedAddress}`;
    }
    return '';
  };

  const addToCart = (item: MenuItem) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.id === item.id);
      if (existing) {
        return prev.map((i) =>
          i.id === item.id ? { ...i, quantity: i.quantity + 1 } : i
        );
      }
      return [...prev, { ...item, quantity: 1 }];
    });
  };

  const removeFromCart = (itemId: string) => {
    setCart((prev) => {
      const existing = prev.find((i) => i.id === itemId);
      if (existing && existing.quantity > 1) {
        return prev.map((i) =>
          i.id === itemId ? { ...i, quantity: i.quantity - 1 } : i
        );
      }
      return prev.filter((i) => i.id !== itemId);
    });
  };

  const getCartTotal = () => {
    const getItemPrice = (item: MenuItem | CartItem) => {
      return item.discounted_price && item.discounted_price < item.price ? item.discounted_price : item.price;
    };
    
    const subtotal = cart.reduce((sum, item) => {
      const itemPrice = getItemPrice(item);
      return sum + itemPrice * item.quantity;
    }, 0);
    const deliveryFee = orderType === 'delivery' && menuData ? menuData.restaurant.delivery_fee : 0;
    return subtotal + deliveryFee;
  };

  const handleSubmitOrder = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!customerName.trim()) {
      alert('Please enter your name');
      return;
    }

    if (orderType === 'delivery' && !deliveryAddress.trim()) {
      alert('Please enter delivery address');
      return;
    }

    // For pickup orders, check if location is confirmed
    if (orderType === 'pickup' && !pickupLocationConfirmed) {
      alert('Please confirm that you can reach the restaurant location to pick up your order.');
      return;
    }

    if (cart.length === 0) {
      alert('Please add items to cart');
      return;
    }

    try {
      // Submit order to backend
      const items = cart.map((item) => ({
        product_id: item.id,
        quantity: item.quantity,
      }));

      const orderData = {
        customer_phone: token || '',
        customer_name: customerName,
        items,
        order_type: orderType,
        delivery_address: orderType === 'delivery' ? deliveryAddress : null,
        // Pass restaurant_id from URL so backend knows which restaurant this order is for
        restaurant_id: restaurantId,
        // Include location coordinates if available
        customer_latitude: customerLat || undefined,
        customer_longitude: customerLon || undefined,
        // Include alternate phone if provided
        alternate_phone: alternatePhone.trim() || undefined,
        // Include payment method
        payment_method: paymentMethod, // "cod" or "online"
      };

      console.log('📤 Submitting order:', orderData);

      const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';
      const response = await fetch(`${API_BASE_URL}/api/v1/orders`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        mode: 'cors',
        body: JSON.stringify(orderData),
      });

      console.log('📥 Order response status:', response.status);

      if (!response.ok) {
        let errorText = '';
        try {
          errorText = await response.text();
          console.error('❌ Order error response:', errorText);
        } catch (e) {
          console.error('❌ Could not read error response');
        }
        
        // Try to parse error as JSON
        let errorMessage = 'Failed to place order';
        try {
          const errorJson = JSON.parse(errorText);
          errorMessage = errorJson.detail || errorMessage;
        } catch (e) {
          errorMessage = errorText || errorMessage;
        }
        
        throw new Error(errorMessage);
      }

      const order = await response.json();
      console.log('✅ Order placed successfully:', order);
      
      // Show success message based on payment method
      if (paymentMethod === 'cod') {
        alert(`✅ Order placed successfully!\n\nOrder ID: ${order.id}\nTotal: ₹${order.total_amount}\nPayment: Cash on Delivery\n\nYou will receive WhatsApp notifications about your order status.`);
      } else {
        // For online payment, show payment link and redirect to payment page
        if (order.payment_link) {
          // Store order info for payment page
          sessionStorage.setItem('pendingOrder', JSON.stringify({
            orderId: order.id,
            totalAmount: order.total_amount || order.total,
            paymentLink: order.payment_link,
            customerName: order.customer_name,
            restaurantId: order.restaurant_id,
            razorpay_payment_link_id: order.razorpay_payment_link_id
          }));
          // Redirect to payment page
          window.location.href = `/payment?order_id=${order.id}`;
        } else {
          alert(`✅ Order received!\n\nOrder ID: ${order.id}\nTotal: ₹${order.total_amount || order.total}\nPayment: Online Payment\n\nCheck your WhatsApp for the payment link. Complete payment to confirm your order.`);
        }
      }
      
      // Reset cart
      setCart([]);
      setShowCheckout(false);
      setCustomerName('');
      setDeliveryAddress('');
      setAlternatePhone('');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to place order. Please try again.';
      alert(`❌ ${errorMessage}\n\nPlease check:\n1. All fields are filled correctly\n2. Items are in cart\n3. Backend server is running`);
      console.error('❌ Order submission error:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 to-indigo-600">
        <div className="text-white text-xl">Loading menu...</div>
      </div>
    );
  }

  if (error || (!loading && !menuData)) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-purple-600 to-indigo-600 p-4">
        <div className="text-center">
          <div className="text-white text-xl mb-4">{error || 'Menu not found'}</div>
          {error && (
            <div className="text-purple-200 text-sm mt-2">
              <p>Please make sure:</p>
              <ul className="list-disc list-inside mt-2 text-left max-w-md mx-auto">
                <li>Backend server is running on http://localhost:4000</li>
                <li>Restaurant ID is correct: <code className="bg-purple-900 px-1 rounded">{restaurantId}</code></li>
                <li>Check browser console (F12) for API URL and error details</li>
                <li>Test backend: Open <a href={`http://localhost:4000/api/public/menu/${restaurantId}`} target="_blank" rel="noopener noreferrer" className="text-yellow-300 underline">this link</a> in a new tab</li>
              </ul>
            </div>
          )}
          <button
            onClick={() => {
              setError('');
              fetchMenu();
            }}
            className="mt-4 bg-white text-purple-600 px-6 py-2 rounded-lg font-semibold hover:bg-purple-50"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-purple-50/20 to-indigo-50/20">
      {/* Enhanced Header with Glassmorphism */}
      <div className="bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-700 text-white shadow-2xl relative overflow-hidden">
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
        }}></div>
        <div className="relative p-4 sm:p-5">
          <div className="flex items-center justify-between">
            <div className="flex-1 pr-16">
              <h1 className="text-lg sm:text-xl md:text-2xl font-bold drop-shadow-lg mb-1">
                🍽️ {menuData.restaurant.name}
              </h1>
              <div className="flex flex-wrap items-center gap-2 text-sm text-purple-100">
                {customerNameFromWhatsApp && (
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                    </svg>
                    {customerNameFromWhatsApp}
                  </span>
                )}
                {locationName && (
                  <span className="flex items-center gap-1">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                    </svg>
                    {locationName}
                  </span>
                )}
                {menuData?.restaurant.address && (
                  <button
                    onClick={() => setShowLocationModal(true)}
                    className="flex items-center gap-1 bg-white/20 hover:bg-white/30 backdrop-blur-md px-3 py-1 rounded-lg transition-all duration-300 border border-white/20"
                    title="View restaurant location"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                    </svg>
                    {distance !== null ? `${distance.toFixed(1)} km away` : 'View Location'}
                  </button>
                )}
              </div>
            </div>
            <button
              onClick={handleBackToRestaurants}
              className="absolute top-4 right-4 bg-white/20 hover:bg-white/30 backdrop-blur-md text-white px-4 py-2 rounded-xl font-bold text-sm transition-all duration-300 flex items-center gap-2 shadow-lg hover:shadow-xl transform hover:scale-105 border border-white/20"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              Back
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 py-6 sm:py-8">
        {/* Menu Categories */}
        {menuData.categories.map((category) => (
          <div key={category.name} className="mb-8 sm:mb-10">
            <div className="flex items-center gap-3 mb-4 sm:mb-5">
              <div className="h-1 w-12 bg-gradient-to-r from-purple-600 to-indigo-600 rounded-full"></div>
              <h2 className="text-xl sm:text-2xl md:text-3xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                {category.name}
              </h2>
              <div className="flex-1 h-1 bg-gradient-to-r from-purple-200 to-transparent rounded-full"></div>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 sm:gap-5">
              {category.items.map((item) => {
                const isAvailable = item.is_available !== false;
                const hasDiscount = item.discounted_price && item.discounted_price < item.price;
                return (
                  <div
                    key={item.id}
                    className={`group relative bg-white rounded-2xl shadow-lg hover:shadow-2xl transition-all duration-300 flex flex-col overflow-hidden border-2 transform hover:-translate-y-1 ${
                      isAvailable 
                        ? 'cursor-pointer border-transparent hover:border-purple-300' 
                        : 'opacity-60 cursor-not-allowed border-gray-200'
                    } ${hasDiscount ? 'bg-gradient-to-br from-green-50/50 to-white' : ''}`}
                  >
                    {/* Discount Badge */}
                    {hasDiscount && (
                      <div className="absolute top-3 right-3 bg-gradient-to-r from-green-500 to-emerald-600 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg z-10">
                        🎯 {item.discount_percentage}% OFF
                      </div>
                    )}
                    
                    {/* Out of Stock Badge */}
                    {!isAvailable && (
                      <div className="absolute top-3 right-3 bg-red-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg z-10">
                        Out of Stock
                      </div>
                    )}

                    <div className="p-4 sm:p-5 flex-1 flex flex-col">
                      {/* Item Name */}
                      <h3 className={`text-base sm:text-lg font-bold line-clamp-2 mb-2 ${
                        isAvailable ? 'text-gray-800' : 'text-gray-400'
                      }`}>
                        {item.name}
                      </h3>
                      
                      {/* Description */}
                      <p className={`text-xs sm:text-sm line-clamp-2 mb-4 flex-grow ${
                        isAvailable ? 'text-gray-600' : 'text-gray-400'
                      }`}>
                        {item.description}
                      </p>
                      
                      {/* Price Section */}
                      <div className="mb-4">
                        {hasDiscount ? (
                          <div className="space-y-2">
                            <div className="flex items-baseline gap-2">
                              <p className="font-bold text-xl sm:text-2xl text-green-600">
                                ₹{item.discounted_price}
                              </p>
                              <p className="text-sm text-gray-400 line-through">
                                ₹{item.price}
                              </p>
                            </div>
                            <span className="inline-block bg-green-100 text-green-700 px-3 py-1 rounded-full text-xs font-bold">
                              Save ₹{((item.price - (item.discounted_price || 0)).toFixed(0))}
                            </span>
                          </div>
                        ) : (
                          <p className={`font-bold text-lg sm:text-xl ${
                            isAvailable ? 'text-purple-600' : 'text-gray-400'
                          }`}>
                            ₹{item.price}
                          </p>
                        )}
                      </div>
                      
                      {/* Add to Cart Button */}
                      <button
                        onClick={() => isAvailable && addToCart(item)}
                        disabled={!isAvailable}
                        className={`w-full py-3 px-4 rounded-xl font-bold text-sm transition-all duration-300 transform ${
                          isAvailable
                            ? 'bg-gradient-to-r from-purple-600 to-indigo-600 text-white hover:from-purple-700 hover:to-indigo-700 shadow-lg hover:shadow-xl group-hover:scale-105'
                            : 'bg-gray-200 text-gray-400 cursor-not-allowed'
                        }`}
                      >
                        {isAvailable ? (
                          <span className="flex items-center justify-center gap-2">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                            </svg>
                            Add to Cart
                          </span>
                        ) : (
                          'Unavailable'
                        )}
                      </button>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}

        {/* Enhanced Floating Cart Button */}
        {cart.length > 0 && (
          <div className="fixed bottom-0 left-0 right-0 bg-white/95 backdrop-blur-md shadow-2xl border-t-2 border-purple-200 p-4 z-40">
            <div className="max-w-7xl mx-auto flex justify-between items-center gap-4">
              <div className="flex items-center gap-4">
                <div className="bg-gradient-to-r from-purple-100 to-indigo-100 rounded-xl p-3">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div>
                  <div className="text-xs sm:text-sm text-gray-600 font-medium">
                    {cart.reduce((sum, item) => sum + item.quantity, 0)} item{cart.reduce((sum, item) => sum + item.quantity, 0) !== 1 ? 's' : ''} in cart
                  </div>
                  <div className="text-xl sm:text-2xl font-bold bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                    ₹{getCartTotal().toFixed(0)}
                  </div>
                </div>
              </div>
              <button
                onClick={() => setShowCheckout(true)}
                className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3 px-8 rounded-xl font-bold hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 text-base sm:text-lg whitespace-nowrap shadow-lg hover:shadow-xl transform hover:scale-105 flex items-center gap-2"
              >
                <span>View Cart & Checkout</span>
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Enhanced Checkout Modal */}
        {showCheckout && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
            <div className="bg-white rounded-3xl max-w-md w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-gray-100">
              {/* Modal Header */}
              <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6 rounded-t-3xl">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold flex items-center gap-2">
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 11-4 0 2 2 0 014 0z" />
                    </svg>
                    Checkout
                  </h2>
                  <button
                    onClick={() => setShowCheckout(false)}
                    className="bg-white/20 hover:bg-white/30 rounded-full p-2 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                <p className="text-purple-100 mt-2 text-sm">Review your order details</p>
              </div>

              <div className="p-6">

                {/* Enhanced Cart Items */}
                <div className="mb-6 space-y-3">
                  {cart.map((item) => (
                    <div key={item.id} className="bg-gray-50 rounded-xl p-4 border border-gray-200">
                      <div className="flex justify-between items-start mb-3">
                        <div className="flex-1">
                          <div className="font-bold text-gray-800 mb-1">{item.name}</div>
                          <div className="text-sm text-gray-600">
                            {item.discounted_price && item.discounted_price < item.price ? (
                              <>
                                <span className="font-bold text-green-600">₹{item.discounted_price}</span>
                                <span className="line-through text-gray-400 ml-2">₹{item.price}</span>
                              </>
                            ) : (
                              <span className="font-semibold">₹{item.price}</span>
                            )}
                            <span className="text-gray-500 ml-1">each</span>
                          </div>
                        </div>
                        <div className="flex items-center gap-3 bg-white rounded-lg px-2 py-1 border border-gray-200">
                          <button
                            onClick={() => removeFromCart(item.id)}
                            className="bg-purple-100 text-purple-700 w-7 h-7 rounded-lg font-bold hover:bg-purple-200 transition-colors flex items-center justify-center"
                          >
                            -
                          </button>
                          <span className="font-bold text-gray-800 min-w-[1.5rem] text-center">{item.quantity}</span>
                          <button
                            onClick={() => addToCart(item)}
                            className="bg-purple-100 text-purple-700 w-7 h-7 rounded-lg font-bold hover:bg-purple-200 transition-colors flex items-center justify-center"
                          >
                            +
                          </button>
                        </div>
                      </div>
                      <div className="text-right">
                        <span className="font-bold text-gray-800">
                          Total: ₹{((item.discounted_price && item.discounted_price < item.price ? item.discounted_price : item.price) * item.quantity).toFixed(0)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Enhanced Order Form */}
                <form onSubmit={handleSubmitOrder} className="space-y-4">
                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Your Name *</label>
                    <input
                      type="text"
                      value={customerName}
                      onChange={(e) => setCustomerName(e.target.value)}
                      className="w-full border-2 border-gray-300 rounded-xl px-4 py-3 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                      required
                      placeholder="Enter your full name"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Mobile Number *</label>
                    <input
                      type="tel"
                      value={token ? (token.startsWith('+') ? token : `+91${token}`) : ''}
                      readOnly
                      className="w-full border-2 border-gray-300 rounded-xl px-4 py-3 bg-gray-100 text-gray-600 cursor-not-allowed"
                      placeholder="Phone number from WhatsApp"
                    />
                    <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z" />
                      </svg>
                      From WhatsApp (auto-filled)
                    </p>
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Alternate Mobile Number (Optional)</label>
                    <input
                      type="tel"
                      value={alternatePhone}
                      onChange={(e) => setAlternatePhone(e.target.value)}
                      className="w-full border-2 border-gray-300 rounded-xl px-4 py-3 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                      placeholder="Enter alternate number if different"
                    />
                    <p className="text-xs text-gray-500 mt-1">💡 For delivery person to contact you</p>
                  </div>

                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-2">Order Type *</label>
                    <select
                      value={orderType}
                      onChange={(e) => setOrderType(e.target.value as 'pickup' | 'delivery')}
                      className="w-full border-2 border-gray-300 rounded-xl px-4 py-3 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all font-semibold"
                      required
                    >
                      <option value="pickup">🏃 Pickup</option>
                      {menuData?.restaurant.delivery_available !== false && (
                        <option value="delivery">🚚 Delivery</option>
                      )}
                    </select>
                    {menuData?.restaurant.delivery_available === false && (
                      <p className="text-xs text-gray-500 mt-1">ℹ️ Delivery is currently unavailable. Only pickup orders are accepted.</p>
                    )}
                  </div>

                  {orderType === 'pickup' && menuData?.restaurant && (
                    <div className="bg-blue-50 border-2 border-blue-200 rounded-xl p-4">
                      <div className="flex items-start gap-3">
                        <div className="bg-blue-100 rounded-full p-2">
                          <svg className="w-5 h-5 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <p className="font-bold text-gray-800 mb-1">📍 Pickup Location</p>
                          <p className="text-sm text-gray-700 mb-2">{menuData.restaurant.address}</p>
                          {distance !== null && (
                            <p className="text-sm text-blue-600 font-semibold mb-2">
                              📏 {distance.toFixed(1)} km away from your location
                            </p>
                          )}
                          {getGoogleMapsLink() && (
                            <a
                              href={getGoogleMapsLink()}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="inline-flex items-center gap-2 bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold text-sm hover:bg-blue-700 transition-colors"
                            >
                              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                              </svg>
                              Open in Google Maps
                            </a>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {orderType === 'delivery' && (
                    <div>
                      <label className="block text-sm font-bold text-gray-700 mb-2">
                        Delivery Address *
                        {deliveryAddress && (
                          <span className="text-green-600 text-xs ml-2 font-normal">✓ Auto-filled from location</span>
                        )}
                      </label>
                      <textarea
                        value={deliveryAddress}
                        onChange={(e) => setDeliveryAddress(e.target.value)}
                        className="w-full border-2 border-gray-300 rounded-xl px-4 py-3 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all"
                        rows={3}
                        required
                        placeholder="Address will be auto-filled from your shared location..."
                      />
                      {deliveryAddress && (
                        <p className="text-xs text-gray-500 mt-1 flex items-center gap-1">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                          </svg>
                          You can edit this address if needed
                        </p>
                      )}
                    </div>
                  )}

                  <div>
                    <label className="block text-sm font-bold text-gray-700 mb-3">Payment Method *</label>
                    <div className="grid grid-cols-2 gap-3">
                      <label className={`relative cursor-pointer border-2 rounded-xl p-4 transition-all ${
                        paymentMethod === 'cod' ? 'border-purple-500 bg-purple-50' : 'border-gray-300 hover:border-gray-400'
                      }`}>
                        <input
                          type="radio"
                          name="payment"
                          value="cod"
                          checked={paymentMethod === 'cod'}
                          onChange={() => setPaymentMethod('cod')}
                          className="sr-only"
                        />
                        <div className="flex flex-col items-center gap-2">
                          <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <span className="font-semibold text-sm">Cash on Delivery</span>
                        </div>
                      </label>
                      <label className={`relative cursor-pointer border-2 rounded-xl p-4 transition-all ${
                        paymentMethod === 'online' ? 'border-purple-500 bg-purple-50' : 'border-gray-300 hover:border-gray-400'
                      }`}>
                        <input
                          type="radio"
                          name="payment"
                          value="online"
                          checked={paymentMethod === 'online'}
                          onChange={() => setPaymentMethod('online')}
                          className="sr-only"
                        />
                        <div className="flex flex-col items-center gap-2">
                          <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                          </svg>
                          <span className="font-semibold text-sm">Online Payment</span>
                        </div>
                      </label>
                    </div>
                  </div>

                  {/* Enhanced Total Section */}
                  <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-2xl p-5 border-2 border-purple-200">
                    <div className="space-y-2 mb-3">
                      <div className="flex justify-between text-gray-700">
                        <span className="font-medium">Subtotal:</span>
                        <span className="font-semibold">₹{cart.reduce((sum, item) => sum + ((item.discounted_price && item.discounted_price < item.price ? item.discounted_price : item.price) * item.quantity), 0).toFixed(0)}</span>
                      </div>
                      {orderType === 'delivery' && (
                        <div className="flex justify-between text-gray-700">
                          <span className="font-medium">Delivery Fee:</span>
                          <span className="font-semibold">₹{menuData.restaurant.delivery_fee}</span>
                        </div>
                      )}
                    </div>
                    <div className="flex justify-between items-center pt-3 border-t-2 border-purple-300">
                      <span className="font-bold text-lg text-gray-800">Total Amount:</span>
                      <span className="font-bold text-2xl bg-gradient-to-r from-purple-600 to-indigo-600 bg-clip-text text-transparent">
                        ₹{getCartTotal().toFixed(0)}
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-3 pt-2">
                    <button
                      type="button"
                      onClick={() => setShowCheckout(false)}
                      className="flex-1 bg-gray-200 text-gray-700 py-3.5 rounded-xl font-bold hover:bg-gray-300 transition-all duration-300"
                    >
                      Back
                    </button>
                    <button
                      type="submit"
                      className="flex-1 bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-3.5 rounded-xl font-bold hover:from-purple-700 hover:to-indigo-700 transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105"
                    >
                      Place Order
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>
        )}

        <style jsx>{`
          @keyframes fadeIn {
            from {
              opacity: 0;
              transform: scale(0.95);
            }
            to {
              opacity: 1;
              transform: scale(1);
            }
          }
          .animate-fadeIn {
            animation: fadeIn 0.3s ease-out;
          }
        `}</style>

        {/* Location Modal */}
        {showLocationModal && menuData?.restaurant && (
          <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4 z-50 animate-fadeIn">
            <div className="bg-white rounded-3xl max-w-md w-full shadow-2xl border border-gray-100">
              <div className="bg-gradient-to-r from-purple-600 to-indigo-600 text-white p-6 rounded-t-3xl">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-bold flex items-center gap-2">
                    <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                    </svg>
                    Restaurant Location
                  </h2>
                  <button
                    onClick={() => setShowLocationModal(false)}
                    className="bg-white/20 hover:bg-white/30 rounded-full p-2 transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>

              <div className="p-6">
                <div className="mb-4">
                  <p className="font-bold text-gray-800 text-lg mb-2">{menuData.restaurant.name}</p>
                  <p className="text-gray-700">{menuData.restaurant.address}</p>
                </div>

                {distance !== null && customerLat && customerLon && (
                  <div className="bg-blue-50 border border-blue-200 rounded-xl p-4 mb-4">
                    <p className="text-sm text-gray-600 mb-1">Distance from your location:</p>
                    <p className="text-2xl font-bold text-blue-600">{distance.toFixed(1)} km</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Estimated travel time: ~{Math.round(distance * 2)} minutes
                    </p>
                  </div>
                )}

                {getGoogleMapsLink() && (
                  <a
                    href={getGoogleMapsLink()}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full bg-gradient-to-r from-blue-600 to-blue-700 text-white py-3 px-6 rounded-xl font-bold hover:from-blue-700 hover:to-blue-800 transition-all duration-300 flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd" />
                    </svg>
                    Open in Google Maps
                  </a>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

