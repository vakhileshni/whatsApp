'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

interface Review {
  order_id: string;
  customer_name: string;
  customer_phone: string;
  rating: number;
  order_date: string;
  total_amount: number;
  items: string;
}

export default function ReviewsPage() {
  const router = useRouter();
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [restaurantInfo, setRestaurantInfo] = useState<any>(null);
  const [stats, setStats] = useState({
    averageRating: 0,
    totalRatings: 0,
    fiveStar: 0,
    fourStar: 0,
    threeStar: 0,
    twoStar: 0,
    oneStar: 0
  });

  useEffect(() => {
    if (!apiClient.isAuthenticated()) {
      router.push('/login');
      return;
    }

    const loadData = async () => {
      try {
        const info = await apiClient.getRestaurantInfo();
        setRestaurantInfo(info);
        
        // Fetch orders with ratings
        const orders = await apiClient.getOrders();
        
        // Filter orders with ratings and format as reviews
        const reviewsData: Review[] = orders
          .filter(order => order.customer_rating !== null && order.customer_rating !== undefined)
          .map(order => ({
            order_id: order.id,
            customer_name: order.customer_name,
            customer_phone: order.customer_phone,
            rating: order.customer_rating || 0,
            order_date: order.created_at,
            total_amount: order.total_amount,
            items: order.items.map(item => `${item.quantity}x ${item.product_name}`).join(', ')
          }))
          .sort((a, b) => new Date(b.order_date).getTime() - new Date(a.order_date).getTime());

        setReviews(reviewsData);

        // Calculate stats
        if (reviewsData.length > 0) {
          const avg = reviewsData.reduce((sum, r) => sum + r.rating, 0) / reviewsData.length;
          const ratingCounts = {
            5: reviewsData.filter(r => r.rating === 5).length,
            4: reviewsData.filter(r => r.rating === 4).length,
            3: reviewsData.filter(r => r.rating === 3).length,
            2: reviewsData.filter(r => r.rating === 2).length,
            1: reviewsData.filter(r => r.rating === 1).length,
          };

          setStats({
            averageRating: avg,
            totalRatings: reviewsData.length,
            fiveStar: ratingCounts[5],
            fourStar: ratingCounts[4],
            threeStar: ratingCounts[3],
            twoStar: ratingCounts[2],
            oneStar: ratingCounts[1]
          });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load reviews');
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, [router]);

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span key={i} className={i < rating ? 'text-yellow-400' : 'text-gray-300'}>
        ⭐
      </span>
    ));
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading reviews...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="w-6 h-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Customer Reviews & Ratings</h1>
                <p className="text-sm text-gray-600">{restaurantInfo?.name || 'Restaurant'}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-lg">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Average Rating</div>
            <div className="flex items-center gap-2">
              <div className="text-3xl font-bold text-gray-900">{stats.averageRating.toFixed(1)}</div>
              <div className="text-yellow-400 text-xl">⭐</div>
            </div>
            <div className="text-xs text-gray-500 mt-1">From {stats.totalRatings} reviews</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">5 Stars</div>
            <div className="text-2xl font-bold text-green-600">{stats.fiveStar}</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">4 Stars</div>
            <div className="text-2xl font-bold text-blue-600">{stats.fourStar}</div>
          </div>

          <div className="bg-white rounded-lg shadow p-4 border border-gray-200">
            <div className="text-sm text-gray-600 mb-1">Total Reviews</div>
            <div className="text-2xl font-bold text-purple-600">{stats.totalRatings}</div>
          </div>
        </div>

        {/* Rating Distribution */}
        <div className="bg-white rounded-lg shadow mb-6 p-6 border border-gray-200">
          <h2 className="text-lg font-bold text-gray-900 mb-4">Rating Distribution</h2>
          <div className="space-y-3">
            {[5, 4, 3, 2, 1].map((stars) => {
              const count = stars === 5 ? stats.fiveStar : 
                           stars === 4 ? stats.fourStar :
                           stars === 3 ? stats.threeStar :
                           stars === 2 ? stats.twoStar : stats.oneStar;
              const percentage = stats.totalRatings > 0 ? (count / stats.totalRatings) * 100 : 0;
              
              return (
                <div key={stars} className="flex items-center gap-3">
                  <div className="w-16 text-sm font-semibold text-gray-700">{stars} Star</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-6 overflow-hidden">
                    <div 
                      className="bg-yellow-400 h-full transition-all duration-500"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <div className="w-12 text-right text-sm font-semibold text-gray-700">{count}</div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Reviews List */}
        <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
          <div className="p-4 border-b border-gray-200 bg-gray-50">
            <h2 className="text-lg font-bold text-gray-900">All Reviews</h2>
          </div>

          {reviews.length === 0 ? (
            <div className="p-12 text-center">
              <div className="text-6xl mb-4">⭐</div>
              <p className="text-lg font-semibold text-gray-700 mb-2">No reviews yet</p>
              <p className="text-gray-500">Customer reviews will appear here once customers rate their orders</p>
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {reviews.map((review) => (
                <div key={review.order_id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-bold text-gray-900">{review.customer_name}</h3>
                        <span className="text-sm text-gray-500">#{review.order_id.slice(-6).toUpperCase()}</span>
                      </div>
                      <p className="text-sm text-gray-600">{review.customer_phone}</p>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center gap-1 mb-1">
                        {renderStars(review.rating)}
                      </div>
                      <p className="text-xs text-gray-500">
                        {new Date(review.order_date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>

                  <div className="mb-3">
                    <p className="text-sm text-gray-700">
                      <span className="font-semibold">Order:</span> {review.items}
                    </p>
                    <p className="text-sm text-gray-600 mt-1">
                      <span className="font-semibold">Amount:</span> ₹{review.total_amount.toFixed(2)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}










