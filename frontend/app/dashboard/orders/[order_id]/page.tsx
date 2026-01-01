'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { apiClient, Order } from '@/lib/api';

export default function OrderDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const orderId = params?.order_id as string;
  
  const [order, setOrder] = useState<Order | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [restaurantInfo, setRestaurantInfo] = useState<any>(null);

  useEffect(() => {
    if (!apiClient.isAuthenticated()) {
      router.push('/login');
      return;
    }

    const loadData = async () => {
      try {
        const [orders, info] = await Promise.all([
          apiClient.getOrders(),
          apiClient.getRestaurantInfo()
        ]);
        
        const foundOrder = orders.find(o => o.id === orderId);
        if (!foundOrder) {
          setError('Order not found');
          return;
        }
        
        setOrder(foundOrder);
        setRestaurantInfo(info);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load order details');
      } finally {
        setLoading(false);
      }
    };

    if (orderId) {
      loadData();
    }
  }, [orderId, router]);

  const handleUpdateOrderStatus = async (newStatus: string) => {
    if (!order) return;
    
    try {
      await apiClient.updateOrderStatus(order.id, newStatus);
      // Reload order data
      const orders = await apiClient.getOrders();
      const updatedOrder = orders.find(o => o.id === orderId);
      if (updatedOrder) {
        setOrder(updatedOrder);
      }
      alert('Order status updated successfully');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update order status');
    }
  };

  const handleCancelOrder = async () => {
    if (!order) return;
    
    if (!confirm('Are you sure you want to cancel this order? The customer will be notified and asked for feedback.')) {
      return;
    }
    
    try {
      await apiClient.updateOrderStatus(order.id, 'cancelled');
      // Reload order data
      const orders = await apiClient.getOrders();
      const updatedOrder = orders.find(o => o.id === orderId);
      if (updatedOrder) {
        setOrder(updatedOrder);
      }
      alert('Order cancelled successfully. Customer has been notified and will be asked for feedback.');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to cancel order');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending': return 'bg-gradient-to-r from-yellow-100 to-yellow-200 text-yellow-900 border-yellow-300';
      case 'preparing': return 'bg-gradient-to-r from-blue-100 to-blue-200 text-blue-900 border-blue-300';
      case 'ready': return 'bg-gradient-to-r from-purple-100 to-purple-200 text-purple-900 border-purple-300';
      case 'delivered': return 'bg-gradient-to-r from-green-100 to-green-200 text-green-900 border-green-300';
      case 'cancelled': return 'bg-gradient-to-r from-red-100 to-red-200 text-red-900 border-red-300';
      default: return 'bg-gray-100 text-gray-900 border-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading order details...</div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-xl text-red-600 mb-4">{error || 'Order not found'}</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
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
                <h1 className="text-2xl font-bold text-gray-900">Order Details</h1>
                <p className="text-sm text-gray-600">{restaurantInfo?.name || 'Restaurant'}</p>
              </div>
            </div>
            <div className={`inline-block px-4 py-2 rounded-full text-sm font-semibold border-2 ${getStatusColor(order.status)}`}>
              {order.status.toUpperCase()}
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {/* Order ID */}
        <div className="bg-white rounded-lg shadow p-4 mb-6 border border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-1">Order ID</p>
              <p className="text-2xl font-bold text-gray-900">#{order.id.slice(-6).toUpperCase()}</p>
            </div>
            <div className="text-right">
              <p className="text-sm font-semibold text-gray-600 uppercase tracking-wide mb-1">Order Date & Time</p>
              <p className="text-base font-semibold text-gray-700">
                {new Date(order.created_at).toLocaleDateString()}
              </p>
              <p className="text-sm font-medium text-gray-600">
                {new Date(order.created_at).toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>

        {/* Customer Information */}
        <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6 border border-blue-200 mb-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">👤 Customer Information</h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">Customer Name</p>
              <p className="text-lg font-bold text-gray-900">{order.customer_name}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">Phone Number</p>
              <p className="text-lg font-semibold text-gray-900">{order.customer_phone}</p>
            </div>
            <div>
              <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">Order Type</p>
              <span className={`inline-block px-3 py-1 text-sm font-semibold rounded ${
                order.order_type === 'Delivery' 
                  ? 'bg-purple-200 text-purple-900' 
                  : 'bg-orange-200 text-orange-900'
              }`}>
                {order.order_type === 'Delivery' ? '🚚 Delivery' : '🏃 Pickup'}
              </span>
            </div>
          </div>
          {order.order_type === 'Delivery' && order.delivery_address && (
            <div className="mt-4 pt-4 border-t border-blue-200">
              <p className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-2">📍 Delivery Address</p>
              <p className="text-sm font-medium text-gray-800 whitespace-pre-line">{order.delivery_address}</p>
            </div>
          )}
        </div>

        {/* Order Items */}
        <div className="bg-white rounded-lg p-6 border-2 border-gray-200 mb-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">🍽️ Order Items</h3>
          <div className="space-y-3">
            {order.items.map((item, idx) => (
              <div key={idx} className="flex justify-between items-center py-3 border-b border-gray-100 last:border-0">
                <div className="flex-1">
                  <p className="font-semibold text-gray-900">{item.quantity}x {item.product_name}</p>
                  <p className="text-sm text-gray-600">₹{item.price.toFixed(2)} each</p>
                </div>
                <p className="font-bold text-gray-900 text-lg">₹{(item.price * item.quantity).toFixed(2)}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Payment Information */}
        <div className="bg-white rounded-lg p-6 border-2 border-gray-200 mb-6">
          <h3 className="text-lg font-bold text-gray-900 mb-4">💳 Payment Information</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Subtotal:</span>
              <span className="font-semibold text-gray-900">₹{order.subtotal.toFixed(2)}</span>
            </div>
            {order.order_type === 'Delivery' && order.delivery_fee > 0 ? (
              <div className="flex justify-between">
                <span className="text-gray-600">Delivery Fee:</span>
                <span className="font-semibold text-purple-700">+ ₹{order.delivery_fee.toFixed(2)}</span>
              </div>
            ) : (
              <div className="flex justify-between">
                <span className="text-gray-600">Pickup:</span>
                <span className="font-semibold text-orange-700">No delivery charge</span>
              </div>
            )}
            <div className="flex justify-between pt-3 border-t-2 border-gray-300">
              <span className="font-bold text-gray-900 text-lg">Total Amount:</span>
              <span className="font-bold text-blue-700 text-xl">₹{order.total.toFixed(2)}</span>
            </div>
            <div className="pt-3 border-t border-gray-200 mt-3">
              <span className={`text-sm font-semibold ${
                order.payment_status === 'verified' ? 'text-green-700' : 
                order.payment_status === 'failed' ? 'text-red-700' : 
                'text-yellow-700'
              }`}>
                Payment: {order.payment_status === 'verified' ? '✓ Verified' : 
                         order.payment_status === 'failed' ? '✕ Failed' : 
                         '⏳ Pending'}
              </span>
              {order.payment_status === 'verified' && order.customer_upi_name && (
                <p className="text-sm text-green-600 mt-1">UPI Name: {order.customer_upi_name}</p>
              )}
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="bg-white rounded-lg p-6 border-2 border-gray-200 space-y-3">
          <h3 className="text-lg font-bold text-gray-900 mb-4">⚡ Actions</h3>
          
          {order.payment_method === 'online' && order.payment_status !== 'verified' && (
            <button
              onClick={() => {
                router.push(`/dashboard?verifyPayment=${order.id}`);
              }}
              className="w-full px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 font-semibold transition-all duration-200 shadow-md"
            >
              💳 Verify Payment
            </button>
          )}
          
          {order.status.toLowerCase() === 'pending' && (
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleUpdateOrderStatus('preparing')}
                className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 font-semibold transition-all duration-200 shadow-md"
              >
                ✓ Mark for Preparing
              </button>
              <button
                onClick={handleCancelOrder}
                className="px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800 font-semibold transition-all duration-200 shadow-md"
              >
                ✕ Cancel Order
              </button>
            </div>
          )}

          {order.status.toLowerCase() === 'preparing' && (
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleUpdateOrderStatus('ready')}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 font-semibold transition-all duration-200 shadow-md"
              >
                ✓ Mark Ready
              </button>
              <button
                onClick={handleCancelOrder}
                className="px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800 font-semibold transition-all duration-200 shadow-md"
              >
                ✕ Cancel Order
              </button>
            </div>
          )}

          {order.status.toLowerCase() === 'ready' && (
            <div className="grid grid-cols-2 gap-3">
              <button
                onClick={() => handleUpdateOrderStatus('delivered')}
                className="px-6 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 font-semibold transition-all duration-200 shadow-md"
              >
                ✓ Mark Delivered
              </button>
              <button
                onClick={handleCancelOrder}
                className="px-6 py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800 font-semibold transition-all duration-200 shadow-md"
              >
                ✕ Cancel Order
              </button>
            </div>
          )}

          {(order.status.toLowerCase() === 'delivered' || order.status.toLowerCase() === 'cancelled') && (
            <div className="text-center py-4">
              <span className={`px-6 py-3 rounded-lg text-base font-semibold ${
                order.status.toLowerCase() === 'delivered' 
                  ? 'bg-green-100 text-green-800' 
                  : 'bg-red-100 text-red-800'
              }`}>
                {order.status.toLowerCase() === 'delivered' ? '✓ Order Completed' : '✕ Order Cancelled'}
              </span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

