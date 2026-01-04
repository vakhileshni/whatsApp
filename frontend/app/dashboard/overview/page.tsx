'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, DashboardStats, Order, Product, RestaurantInfo } from '@/lib/api';

export default function OverviewPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [menu, setMenu] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [restaurantInfo, setRestaurantInfo] = useState<RestaurantInfo | null>(null);

  useEffect(() => {
    if (!apiClient.isAuthenticated()) {
      router.push('/login');
      return;
    }
    
    const loadData = async () => {
      try {
        setLoading(true);
        const [info, statsData, ordersData, menuData] = await Promise.all([
          apiClient.getRestaurantInfo().catch(() => null),
          apiClient.getDashboardStats(),
          apiClient.getOrders(),
          apiClient.getMenu()
        ]);
        
        setRestaurantInfo(info);
        setStats(statsData);
        setOrders(ordersData);
        setMenu(menuData);
      } catch (err) {
        console.error('Failed to load data:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadData();
  }, [router]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex items-center justify-center">
        <p className="text-red-600">Failed to load dashboard data</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
          <div className="flex justify-between items-center min-h-16 py-2 sm:py-0">
            <div className="flex items-center flex-1 min-w-0">
              <button
                onClick={() => router.push('/dashboard')}
                className="h-8 w-8 sm:h-10 sm:w-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mr-2 sm:mr-3 flex-shrink-0 hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 cursor-pointer active:scale-95"
                title="Back to Dashboard"
              >
                <svg className="h-5 w-5 sm:h-6 sm:w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
              </button>
              <div className="min-w-0 flex-1">
                <h1 className="text-base sm:text-xl lg:text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent flex flex-wrap items-center gap-1.5 sm:gap-2 lg:gap-3">
                  <span className="whitespace-nowrap">📊 Dashboard Overview</span>
                  {restaurantInfo && (
                    <>
                      <span className="text-gray-400">•</span>
                      <span className="text-sm sm:text-base lg:text-lg font-semibold text-gray-700">{restaurantInfo.name}</span>
                    </>
                  )}
                </h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => router.push('/dashboard')}
                className="flex items-center px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200"
              >
                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 sm:py-6 lg:py-8">
        <div className="space-y-6">
          {/* Key Metrics Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-white bg-opacity-20 rounded-lg">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <span className="text-blue-100 text-sm">Total</span>
              </div>
              <h3 className="text-3xl font-bold mb-1">{stats.total_orders}</h3>
              <p className="text-blue-100 text-sm">All-time orders</p>
            </div>

            <div className="bg-gradient-to-br from-green-500 to-green-600 rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-white bg-opacity-20 rounded-lg">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <span className="text-green-100 text-sm">Revenue</span>
              </div>
              <h3 className="text-3xl font-bold mb-1">₹{stats.total_revenue.toFixed(0)}</h3>
              <p className="text-green-100 text-sm">Total earnings</p>
            </div>

            <div className="bg-gradient-to-br from-purple-500 to-purple-600 rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-white bg-opacity-20 rounded-lg">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <span className="text-purple-100 text-sm">Avg. Order</span>
              </div>
              <h3 className="text-3xl font-bold mb-1">
                ₹{stats.total_orders > 0 ? (stats.total_revenue / stats.total_orders).toFixed(0) : '0'}
              </h3>
              <p className="text-purple-100 text-sm">Per order value</p>
            </div>

            <div className="bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl p-6 text-white shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-white bg-opacity-20 rounded-lg">
                  <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <span className="text-orange-100 text-sm">Menu Items</span>
              </div>
              <h3 className="text-3xl font-bold mb-1">{menu.length}</h3>
              <p className="text-orange-100 text-sm">{menu.filter(m => m.is_available).length} available</p>
            </div>
          </div>

          {/* Order Status Overview */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-600">Pending Orders</h3>
                <div className="p-2 bg-yellow-100 rounded-lg">
                  <svg className="h-5 w-5 text-yellow-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-2xl font-bold text-gray-900">{stats.pending_orders}</p>
              <p className="text-xs text-gray-500 mt-1">Requires action</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-600">Preparing</h3>
                <div className="p-2 bg-blue-100 rounded-lg">
                  <svg className="h-5 w-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {orders.filter(o => o.status.toLowerCase() === 'preparing').length}
              </p>
              <p className="text-xs text-gray-500 mt-1">In kitchen</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-600">Ready</h3>
                <div className="p-2 bg-green-100 rounded-lg">
                  <svg className="h-5 w-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <p className="text-2xl font-bold text-gray-900">
                {orders.filter(o => o.status.toLowerCase() === 'ready').length}
              </p>
              <p className="text-xs text-gray-500 mt-1">Ready for pickup</p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-semibold text-gray-600">Today's Orders</h3>
                <div className="p-2 bg-indigo-100 rounded-lg">
                  <svg className="h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
              <p className="text-2xl font-bold text-gray-900">{stats.today_orders}</p>
              <p className="text-xs text-gray-500 mt-1">Orders received today</p>
            </div>
          </div>

          {/* Menu Analytics */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Menu Overview</h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Total Items</span>
                  <span className="text-xl font-bold text-gray-900">{menu.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Available</span>
                  <span className="text-xl font-bold text-green-600">{menu.filter(m => m.is_available).length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-600">Out of Stock</span>
                  <span className="text-xl font-bold text-red-600">{menu.filter(m => !m.is_available).length}</span>
                </div>
                <div className="pt-4 border-t border-gray-200">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Availability Rate</span>
                    <span className="text-sm font-semibold text-gray-900">
                      {menu.length > 0 ? ((menu.filter(m => m.is_available).length / menu.length) * 100).toFixed(1) : 0}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all duration-300"
                      style={{
                        width: `${menu.length > 0 ? (menu.filter(m => m.is_available).length / menu.length) * 100 : 0}%`
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Top Categories</h3>
              <div className="space-y-3">
                {(() => {
                  const categoryCounts: { [key: string]: number } = {};
                  menu.forEach(item => {
                    categoryCounts[item.category] = (categoryCounts[item.category] || 0) + 1;
                  });
                  const topCategories = Object.entries(categoryCounts)
                    .sort(([, a], [, b]) => b - a)
                    .slice(0, 5);

                  return topCategories.length > 0 ? (
                    topCategories.map(([category, count]) => (
                      <div key={category} className="flex items-center justify-between">
                        <span className="text-sm text-gray-700">{category}</span>
                        <div className="flex items-center gap-3">
                          <div className="w-24 bg-gray-200 rounded-full h-2">
                            <div
                              className="bg-blue-500 h-2 rounded-full"
                              style={{ width: `${(count / menu.length) * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-semibold text-gray-900 w-8 text-right">{count}</span>
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-sm text-gray-500">No categories yet</p>
                  );
                })()}
              </div>
            </div>
          </div>

          {/* Order Trends */}
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Order Activity</h3>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Order ID</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Customer</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Time</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {orders.slice(0, 10).map((order) => (
                    <tr key={order.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3 whitespace-nowrap text-sm font-medium text-gray-900">
                        {order.id}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-900">
                        {order.customer_name}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap">
                        <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          order.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                          order.status === 'preparing' ? 'bg-blue-100 text-blue-800' :
                          order.status === 'ready' ? 'bg-green-100 text-green-800' :
                          order.status === 'delivered' ? 'bg-gray-100 text-gray-800' :
                          'bg-red-100 text-red-800'
                        }`}>
                          {order.status.toUpperCase()}
                        </span>
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm font-semibold text-gray-900">
                        ₹{order.total_amount.toFixed(2)}
                      </td>
                      <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-500">
                        {new Date(order.created_at).toLocaleTimeString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
              {orders.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  <p>No orders yet</p>
                </div>
              )}
            </div>
            {orders.length > 10 && (
              <div className="mt-4 text-center">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="text-blue-600 hover:text-blue-700 font-medium text-sm"
                >
                  View All Orders →
                </button>
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button
              onClick={() => router.push('/dashboard')}
              className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl p-6 shadow-lg hover:from-blue-600 hover:to-blue-700 transition-all duration-200 text-left"
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold">Manage Orders</h3>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <p className="text-blue-100 text-sm">View and process all orders</p>
            </button>

            <button
              onClick={() => router.push('/dashboard')}
              className="bg-gradient-to-r from-green-500 to-green-600 text-white rounded-xl p-6 shadow-lg hover:from-green-600 hover:to-green-700 transition-all duration-200 text-left"
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold">Manage Menu</h3>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                </svg>
              </div>
              <p className="text-green-100 text-sm">Add, edit, and manage menu items</p>
            </button>

            <button
              onClick={() => router.push('/dashboard/reviews')}
              className="bg-gradient-to-r from-purple-500 to-purple-600 text-white rounded-xl p-6 shadow-lg hover:from-purple-600 hover:to-purple-700 transition-all duration-200 text-left"
            >
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold">View Reviews</h3>
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
              </div>
              <p className="text-purple-100 text-sm">Check customer ratings and feedback</p>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}




