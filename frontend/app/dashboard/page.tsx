'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, DashboardStats, Order, Product, RestaurantInfo } from '@/lib/api';

export default function DashboardPage() {
  const router = useRouter();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [menu, setMenu] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'orders' | 'menu'>('orders');
  const [error, setError] = useState('');
  const [restaurantInfo, setRestaurantInfo] = useState<RestaurantInfo | null>(null);
  const [showProductModal, setShowProductModal] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [productForm, setProductForm] = useState({
    name: '',
    description: '',
    price: '',
    category: '',
    is_available: true
  });
  const [orderFilter, setOrderFilter] = useState<'all' | 'pending' | 'preparing' | 'ready' | 'delivered'>('all');
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [showOrderDetails, setShowOrderDetails] = useState(false);
  const [showQRCode, setShowQRCode] = useState(false);
  const [showUPIModal, setShowUPIModal] = useState(false);
  const [upiForm, setUpiForm] = useState({ upi_id: '', password: '' });
  const [showPaymentVerify, setShowPaymentVerify] = useState(false);
  const [paymentUpiName, setPaymentUpiName] = useState('');
  const [showUPIVerify, setShowUPIVerify] = useState(false);
  const [upiVerifyData, setUpiVerifyData] = useState<{upi_id: string; qr_data: string; amount: number} | null>(null);

  useEffect(() => {
    if (!apiClient.isAuthenticated()) {
      router.push('/login');
      return;
    }
    
    // Fetch restaurant info from backend
    const loadRestaurantInfo = async () => {
      try {
        const info = await apiClient.getRestaurantInfo();
        setRestaurantInfo(info);
      } catch (err) {
        console.error('Failed to load restaurant info:', err);
        // Fallback to localStorage if API fails
        const localInfo = apiClient.getRestaurantInfoFromStorage();
        if (localInfo) {
          setRestaurantInfo({ 
            name: localInfo.name, 
            id: localInfo.id, 
            phone: localInfo.phone, 
            upi_id: '',
            twilio_number: '14155238886' // Default fallback
          });
        }
      }
    };
    
    loadRestaurantInfo();
    fetchData();
  }, [router]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [statsData, ordersData, menuData] = await Promise.all([
        apiClient.getDashboardStats(),
        apiClient.getOrders(),
        apiClient.getMenu()
      ]);
      setStats(statsData);
      setOrders(ordersData);
      setMenu(menuData);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    apiClient.logout();
    router.push('/login');
  };

  const handleUpdateOrderStatus = async (orderId: string, newStatus: string) => {
    try {
      await apiClient.updateOrderStatus(orderId, newStatus);
      await fetchData();
      // Close order details modal if it's open
      if (showOrderDetails) {
        setShowOrderDetails(false);
        setSelectedOrder(null);
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update order status');
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    if (!confirm('Are you sure you want to cancel this order? The customer will be notified and refund will be processed.')) {
      return;
    }
    try {
      await apiClient.updateOrderStatus(orderId, 'cancelled');
      await fetchData();
      setShowOrderDetails(false);
      setSelectedOrder(null);
      alert('Order cancelled successfully. Customer has been notified.');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to cancel order');
    }
  };

  const handleVerifyUPI = async () => {
    if (!upiForm.upi_id.trim()) {
      alert('Please enter a UPI ID to verify');
      return;
    }
    if (!upiForm.password.trim()) {
      alert('Please enter your password');
      return;
    }
    
    // Client-side UPI format validation
    const upiId = upiForm.upi_id.trim();
    const upiPattern = /^[a-zA-Z0-9][a-zA-Z0-9._-]*@[a-zA-Z0-9]+$/;
    if (!upiPattern.test(upiId)) {
      alert('Invalid UPI ID format. Please use format: username@bank or phone@upi\n\nExamples:\n• restaurant@paytm\n• 1234567890@upi\n• username@ybl');
      return;
    }
    
    try {
      const verifyResponse = await apiClient.verifyRestaurantUPI(upiId, upiForm.password);
      setUpiVerifyData({
        upi_id: verifyResponse.upi_id,
        qr_data: verifyResponse.qr_data,
        amount: verifyResponse.verification_amount
      });
      setShowUPIVerify(true);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to verify UPI ID');
    }
  };

  const handleConfirmUPIVerification = async () => {
    if (!upiVerifyData) return;
    
    const confirmed = confirm(
      `Have you successfully sent ₹${upiVerifyData.amount.toFixed(2)} to ${upiVerifyData.upi_id}?\n\n` +
      'If yes, the UPI ID will be saved. If no, please check the UPI ID and try again.'
    );
    
    if (confirmed) {
      try {
        const updated = await apiClient.updateRestaurantUPI(upiVerifyData.upi_id, upiForm.password);
        setRestaurantInfo(updated);
        setShowUPIModal(false);
        setShowUPIVerify(false);
        setUpiForm({ upi_id: '', password: '' });
        setUpiVerifyData(null);
        alert('✅ UPI ID verified and saved successfully!');
      } catch (err) {
        alert(err instanceof Error ? err.message : 'Failed to save UPI ID');
      }
    }
  };

  const handleUpdateUPI = async (e: React.FormEvent) => {
    e.preventDefault();
    // Instead of directly updating, show verification flow
    await handleVerifyUPI();
  };

  const handleVerifyPayment = async () => {
    if (!selectedOrder) return;
    if (!paymentUpiName.trim()) {
      alert('Please enter customer UPI name');
      return;
    }
    try {
      await apiClient.verifyPayment(selectedOrder.id, paymentUpiName.trim());
      await fetchData();
      // Update selected order
      const updatedOrder = orders.find(o => o.id === selectedOrder.id);
      if (updatedOrder) {
        setSelectedOrder(updatedOrder);
      }
      setShowPaymentVerify(false);
      setPaymentUpiName('');
      alert('Payment verified successfully!');
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to verify payment');
    }
  };

  const handleViewOrderDetails = (order: Order) => {
    setSelectedOrder(order);
    setShowOrderDetails(true);
  };

  const formatPhoneForWhatsApp = (phone: string): string => {
    // Remove any non-numeric characters except +
    const cleaned = phone.replace(/[^\d+]/g, '');
    // If it doesn't start with +, add +91 (India country code)
    if (!cleaned.startsWith('+')) {
      return `91${cleaned}`;
    }
    return cleaned.replace('+', '');
  };

  const getWhatsAppUrl = (phone: string, message?: string): string => {
    const formattedPhone = formatPhoneForWhatsApp(phone);
    const defaultMessage = `Hi! This is regarding your order.`;
    const urlMessage = message || defaultMessage;
    return `https://wa.me/${formattedPhone}?text=${encodeURIComponent(urlMessage)}`;
  };

  const handleAddProduct = () => {
    setEditingProduct(null);
    setProductForm({
      name: '',
      description: '',
      price: '',
      category: '',
      is_available: true
    });
    setShowProductModal(true);
  };

  const handleEditProduct = (product: Product) => {
    setEditingProduct(product);
    setProductForm({
      name: product.name,
      description: product.description,
      price: product.price.toString(),
      category: product.category,
      is_available: product.is_available
    });
    setShowProductModal(true);
  };

  const handleDeleteProduct = async (productId: string, productName: string) => {
    if (!confirm(`Are you sure you want to delete "${productName}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await apiClient.deleteProduct(productId);
      await fetchData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to delete product');
    }
  };

  const handleToggleAvailability = async (product: Product) => {
    try {
      await apiClient.updateProduct(product.id, {
        is_available: !product.is_available
      });
      await fetchData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to update product availability');
    }
  };

  const handleSaveProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingProduct) {
        await apiClient.updateProduct(editingProduct.id, {
          name: productForm.name,
          description: productForm.description,
          price: parseFloat(productForm.price),
          category: productForm.category,
          is_available: productForm.is_available
        });
      } else {
        await apiClient.createProduct({
          name: productForm.name,
          description: productForm.description,
          price: parseFloat(productForm.price),
          category: productForm.category,
          is_available: productForm.is_available
        });
      }
      
      setShowProductModal(false);
      await fetchData();
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to save product');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'pending': return 'bg-gradient-to-r from-yellow-100 to-yellow-200 text-yellow-900 border-yellow-300';
      case 'preparing': return 'bg-gradient-to-r from-blue-100 to-blue-200 text-blue-900 border-blue-300';
      case 'ready': return 'bg-gradient-to-r from-purple-100 to-purple-200 text-purple-900 border-purple-300';
      case 'delivered': return 'bg-gradient-to-r from-green-100 to-green-200 text-green-900 border-green-300';
      case 'cancelled': return 'bg-gradient-to-r from-red-100 to-red-200 text-red-900 border-red-300';
      default: return 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-900 border-gray-300';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-600 text-lg">Loading dashboard...</p>
        </div>
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
                onClick={() => setShowQRCode(true)}
                className="h-8 w-8 sm:h-10 sm:w-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl flex items-center justify-center mr-2 sm:mr-3 flex-shrink-0 hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 cursor-pointer active:scale-95"
                title="Show WhatsApp QR Code"
              >
                <svg className="h-5 w-5 sm:h-6 sm:w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
                </svg>
              </button>
              <div className="min-w-0 flex-1">
                <h1 className="text-base sm:text-xl lg:text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent flex flex-wrap items-center gap-1.5 sm:gap-2 lg:gap-3">
                  <span className="whitespace-nowrap">Dashboard</span>
                  {restaurantInfo && (
                    <>
                      <span className="text-gray-400">•</span>
                      <span className="text-sm sm:text-base lg:text-lg font-semibold text-gray-700">{restaurantInfo.name}</span>
                      <span className="text-xs sm:text-sm font-medium text-gray-500 px-1.5 sm:px-2 py-0.5 sm:py-1 bg-gray-100 rounded whitespace-nowrap">ID: {restaurantInfo.id}</span>
                    </>
                  )}
                </h1>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => {
                  setUpiForm({ upi_id: restaurantInfo?.upi_id || '', password: '' });
                  setShowUPIModal(true);
                }}
                className="flex items-center px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200 flex-shrink-0"
                title="Manage UPI Payment Details"
              >
                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span className="hidden sm:inline">UPI</span>
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center px-3 sm:px-4 py-2 text-xs sm:text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition duration-200 flex-shrink-0"
              >
                <svg className="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                Logout
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8 py-4 sm:py-6 lg:py-8">
        {error && (
          <div className="mb-6 bg-red-50 border-l-4 border-red-500 p-4 rounded-lg shadow-sm">
            <div className="flex">
              <svg className="h-5 w-5 text-red-400 mr-3" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
              <p className="text-red-800">{error}</p>
            </div>
          </div>
        )}

        {/* Compact Stats Cards */}
        {stats && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 sm:gap-3 mb-4 sm:mb-6">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-3 sm:p-4 border border-blue-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-blue-700 mb-1">Total Orders</p>
                  <p className="text-xl sm:text-2xl font-bold text-blue-900">{stats.total_orders}</p>
                </div>
                <div className="p-1.5 sm:p-2 bg-blue-200 rounded-lg">
                  <svg className="h-4 w-4 sm:h-5 sm:w-5 text-blue-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg p-3 sm:p-4 border border-yellow-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-yellow-700 mb-1">Pending</p>
                  <p className="text-xl sm:text-2xl font-bold text-yellow-900">{stats.pending_orders}</p>
                </div>
                <div className="p-1.5 sm:p-2 bg-yellow-200 rounded-lg">
                  <svg className="h-4 w-4 sm:h-5 sm:w-5 text-yellow-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg p-3 sm:p-4 border border-indigo-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-indigo-700 mb-1">Today</p>
                  <p className="text-xl sm:text-2xl font-bold text-indigo-900">{stats.today_orders}</p>
                </div>
                <div className="p-1.5 sm:p-2 bg-indigo-200 rounded-lg">
                  <svg className="h-4 w-4 sm:h-5 sm:w-5 text-indigo-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-3 sm:p-4 border border-green-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-medium text-green-700 mb-1">Revenue</p>
                  <p className="text-xl sm:text-2xl font-bold text-green-900">₹{stats.total_revenue.toFixed(0)}</p>
                </div>
                <div className="p-1.5 sm:p-2 bg-green-200 rounded-lg">
                  <svg className="h-4 w-4 sm:h-5 sm:w-5 text-green-700" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              <button
                onClick={() => setActiveTab('orders')}
                className={`px-8 py-4 text-sm font-semibold border-b-2 transition-colors duration-200 ${
                  activeTab === 'orders'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="flex items-center">
                  <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  Orders
                </span>
              </button>
              <button
                onClick={() => setActiveTab('menu')}
                className={`px-8 py-4 text-sm font-semibold border-b-2 transition-colors duration-200 ${
                  activeTab === 'menu'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="flex items-center">
                  <svg className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  Menu
                </span>
              </button>
            </nav>
          </div>
        </div>

        {/* Orders Tab - Card/Box Layout */}
        {activeTab === 'orders' && (
          <div className="space-y-4">
            {/* Filter Buttons */}
            <div className="bg-white rounded-xl shadow-md border border-gray-200 p-3 sm:p-4">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg sm:text-xl font-bold text-gray-900 flex items-center">
                  <svg className="h-5 w-5 sm:h-6 sm:w-6 mr-2 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <span className="hidden sm:inline">Orders</span>
                </h2>
                <span className="px-2 sm:px-3 py-1 bg-blue-100 text-blue-800 text-xs sm:text-sm font-semibold rounded-full">
                  {orders.length} {orders.length === 1 ? 'order' : 'orders'}
                </span>
              </div>
              <div className="flex gap-1.5 sm:gap-2 flex-wrap">
                <button
                  onClick={() => setOrderFilter('all')}
                  className={`px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                    orderFilter === 'all'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  All ({orders.length})
                </button>
                <button
                  onClick={() => setOrderFilter('pending')}
                  className={`px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                    orderFilter === 'pending'
                      ? 'bg-yellow-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Pending ({orders.filter(o => o.status.toLowerCase() === 'pending').length})
                </button>
                <button
                  onClick={() => setOrderFilter('preparing')}
                  className={`px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                    orderFilter === 'preparing'
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Preparing ({orders.filter(o => o.status.toLowerCase() === 'preparing').length})
                </button>
                <button
                  onClick={() => setOrderFilter('ready')}
                  className={`px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                    orderFilter === 'ready'
                      ? 'bg-purple-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Ready ({orders.filter(o => o.status.toLowerCase() === 'ready').length})
                </button>
                <button
                  onClick={() => setOrderFilter('delivered')}
                  className={`px-2.5 sm:px-4 py-1.5 sm:py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all ${
                    orderFilter === 'delivered'
                      ? 'bg-green-600 text-white shadow-md'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Completed ({orders.filter(o => o.status.toLowerCase() === 'delivered').length})
                </button>
              </div>
            </div>

            {/* Orders Grid - Card Layout */}
            {orders.length === 0 ? (
              <div className="bg-white rounded-xl shadow-md border border-gray-200 p-8 sm:p-16 text-center">
                <div className="inline-flex items-center justify-center w-20 h-20 bg-gray-100 rounded-full mb-4">
                  <svg className="h-10 w-10 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <p className="text-gray-600 text-lg font-semibold mb-2">No orders yet</p>
                <p className="text-gray-400 text-sm">Orders will appear here when customers place orders via WhatsApp</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                {orders
                  .filter(order => orderFilter === 'all' || order.status.toLowerCase() === orderFilter)
                  .map((order) => (
                    <div 
                      key={order.id} 
                      onClick={() => handleViewOrderDetails(order)}
                      className="bg-white rounded-xl shadow-lg border-2 border-gray-200 hover:border-blue-400 hover:shadow-xl transition-all duration-200 overflow-hidden cursor-pointer"
                    >
                      {/* Order Header */}
                      <div className={`p-3 sm:p-4 border-b-2 ${
                        order.status.toLowerCase() === 'pending' ? 'bg-gradient-to-r from-yellow-50 to-yellow-100 border-yellow-300' :
                        order.status.toLowerCase() === 'preparing' ? 'bg-gradient-to-r from-blue-50 to-blue-100 border-blue-300' :
                        order.status.toLowerCase() === 'ready' ? 'bg-gradient-to-r from-purple-50 to-purple-100 border-purple-300' :
                        'bg-gradient-to-r from-green-50 to-green-100 border-green-300'
                      }`}>
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex items-center gap-2">
                            <div className={`w-2.5 h-2.5 sm:w-3 sm:h-3 rounded-full ${
                              order.status.toLowerCase() === 'pending' ? 'bg-yellow-500 animate-pulse' :
                              order.status.toLowerCase() === 'preparing' ? 'bg-blue-500 animate-pulse' :
                              order.status.toLowerCase() === 'ready' ? 'bg-purple-500 animate-pulse' :
                              'bg-green-500'
                            }`}></div>
                            <h3 className="text-base sm:text-lg font-bold text-gray-900">#{order.id.slice(-6).toUpperCase()}</h3>
                          </div>
                          <span className={`px-2 sm:px-3 py-0.5 sm:py-1 text-xs font-bold rounded-full shadow-sm ${getStatusColor(order.status)}`}>
                            {order.status.toUpperCase()}
                          </span>
                        </div>
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className={`px-2 py-0.5 sm:py-1 text-xs font-semibold rounded ${
                            order.order_type === 'Delivery' 
                              ? 'bg-purple-200 text-purple-900' 
                              : 'bg-orange-200 text-orange-900'
                          }`}>
                            {order.order_type === 'Delivery' ? '🚚 Delivery' : '🏃 Pickup'}
                          </span>
                          <span className="text-xs text-gray-600">
                            {new Date(order.created_at).toLocaleTimeString()}
                          </span>
                        </div>
                      </div>

                      {/* Order Body */}
                      <div className="p-3 sm:p-4 space-y-2 sm:space-y-3">
                        {/* Customer Info */}
                        <div className="space-y-2">
                          <div className="flex items-center text-sm">
                            <svg className="h-4 w-4 mr-2 text-blue-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                            </svg>
                            <span className="font-semibold text-gray-900">{order.customer_name}</span>
                          </div>
                          <div className="flex items-center text-sm text-gray-600">
                            <svg className="h-4 w-4 mr-2 text-green-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                            </svg>
                            {order.customer_phone}
                          </div>
                          {order.delivery_address && (
                            <div className="flex items-start text-xs text-gray-600 bg-gray-50 p-2 rounded">
                              <svg className="h-3 w-3 mr-1 mt-0.5 text-gray-500 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                              </svg>
                              <span className="line-clamp-2">{order.delivery_address}</span>
                            </div>
                          )}
                        </div>

                        {/* Order Type - Prominent Display */}
                        <div className={`rounded-lg p-2 sm:p-3 border-2 ${
                          order.order_type.toLowerCase() === 'delivery' 
                            ? 'bg-purple-50 border-purple-300' 
                            : 'bg-orange-50 border-orange-300'
                        }`}>
                          <div className="flex items-center justify-between flex-wrap gap-2">
                            <div className="flex items-center gap-2">
                              {order.order_type.toLowerCase() === 'delivery' ? (
                                <svg className="h-4 w-4 sm:h-5 sm:w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                </svg>
                              ) : (
                                <svg className="h-4 w-4 sm:h-5 sm:w-5 text-orange-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                                </svg>
                              )}
                              <span className={`font-bold text-xs sm:text-sm ${
                                order.order_type.toLowerCase() === 'delivery' 
                                  ? 'text-purple-800' 
                                  : 'text-orange-800'
                              }`}>
                                {order.order_type === 'Delivery' ? '🚚 Delivery' : '🏃 Pickup'}
                              </span>
                            </div>
                            {order.order_type.toLowerCase() === 'delivery' && order.delivery_address && (
                              <span className="text-xs text-purple-700 font-medium">📍 Address</span>
                            )}
                          </div>
                        </div>

                        {/* Order Items */}
                        <div className="bg-gray-50 rounded-lg p-2 sm:p-3 border border-gray-200">
                          <div className="text-xs font-semibold text-gray-700 mb-2">Order Items:</div>
                          <div className="space-y-1">
                            {order.items.map((item, idx) => (
                              <div key={idx} className="flex justify-between text-xs text-gray-700">
                                <span><span className="font-bold text-blue-600">{item.quantity}x</span> {item.product_name}</span>
                                <span className="font-semibold">₹{(item.price * item.quantity).toFixed(2)}</span>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Payment Status */}
                        <div className={`rounded-lg p-3 border-2 ${
                          order.payment_status === 'verified' 
                            ? 'bg-green-50 border-green-300' 
                            : order.payment_status === 'failed'
                            ? 'bg-red-50 border-red-300'
                            : 'bg-yellow-50 border-yellow-300'
                        }`}>
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-2">
                              <svg className={`h-5 w-5 ${
                                order.payment_status === 'verified' ? 'text-green-600' : 
                                order.payment_status === 'failed' ? 'text-red-600' : 'text-yellow-600'
                              }`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              <span className={`font-semibold text-sm ${
                                order.payment_status === 'verified' ? 'text-green-800' : 
                                order.payment_status === 'failed' ? 'text-red-800' : 'text-yellow-800'
                              }`}>
                                Payment: {order.payment_status === 'verified' ? '✓ Verified' : 
                                         order.payment_status === 'failed' ? '✕ Failed' : '⏳ Pending'}
                              </span>
                            </div>
                            {order.payment_status === 'verified' && order.customer_upi_name && (
                              <span className="text-xs text-green-700 font-medium">
                                {order.customer_upi_name}
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Price Breakdown */}
                        <div className="bg-white rounded-lg p-3 border-2 border-gray-200 space-y-2">
                          <div className="flex justify-between text-sm">
                            <span className="text-gray-600">Subtotal:</span>
                            <span className="font-semibold text-gray-900">₹{order.subtotal.toFixed(2)}</span>
                          </div>
                          {order.order_type.toLowerCase() === 'delivery' && order.delivery_fee > 0 ? (
                            <div className="flex justify-between text-sm border-t border-gray-200 pt-2">
                              <span className="text-purple-700 font-medium">Delivery Charge:</span>
                              <span className="font-bold text-purple-700">+ ₹{order.delivery_fee.toFixed(2)}</span>
                            </div>
                          ) : (
                            <div className="flex justify-between text-sm border-t border-gray-200 pt-2">
                              <span className="text-orange-700 font-medium">Pickup:</span>
                              <span className="font-semibold text-orange-700">No delivery charge</span>
                            </div>
                          )}
                          <div className="flex justify-between text-base font-bold border-t-2 border-gray-300 pt-2">
                            <span className="text-gray-900">Total Amount:</span>
                            <span className="text-blue-700">₹{order.total.toFixed(2)}</span>
                          </div>
                        </div>
                      </div>

                      {/* Quick Action Buttons */}
                      <div className="p-4 bg-gray-50 border-t border-gray-200 space-y-2">
                        {/* Payment Verification Button */}
                        {order.payment_status !== 'verified' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setSelectedOrder(order);
                              setShowPaymentVerify(true);
                            }}
                            className="w-full px-4 py-2.5 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 text-sm font-bold transition-all duration-200 shadow-md hover:shadow-lg"
                          >
                            💳 Verify Payment
                          </button>
                        )}
                        {order.status.toLowerCase() === 'pending' && (
                          <div className="grid grid-cols-2 gap-2">
                            <button
                              onClick={() => handleUpdateOrderStatus(order.id, 'preparing')}
                              className="w-full px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 text-sm font-bold transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                            >
                              ✓ Mark for Preparing
                            </button>
                            <button
                              onClick={(e) => { e.stopPropagation(); handleUpdateOrderStatus(order.id, 'cancelled'); }}
                              className="w-full px-3 sm:px-4 py-2.5 sm:py-3 bg-gradient-to-r from-red-600 to-red-700 text-white rounded-lg hover:from-red-700 hover:to-red-800 text-xs sm:text-sm font-bold transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                            >
                              ✕ Cancel
                            </button>
                          </div>
                        )}
                        {order.status.toLowerCase() === 'preparing' && (
                          <button
                            onClick={(e) => { e.stopPropagation(); handleUpdateOrderStatus(order.id, 'ready'); }}
                            className="w-full px-3 sm:px-4 py-2.5 sm:py-3 bg-gradient-to-r from-purple-600 to-purple-700 text-white rounded-lg hover:from-purple-700 hover:to-purple-800 text-xs sm:text-sm font-bold transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                          >
                            ✓ Mark Ready
                          </button>
                        )}
                        {order.status.toLowerCase() === 'ready' && (
                          <button
                            onClick={(e) => { e.stopPropagation(); handleUpdateOrderStatus(order.id, 'delivered'); }}
                            className="w-full px-3 sm:px-4 py-2.5 sm:py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-lg hover:from-green-700 hover:to-green-800 text-xs sm:text-sm font-bold transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105"
                          >
                            ✓ Deliver
                          </button>
                        )}
                        {order.status.toLowerCase() === 'delivered' && (
                          <div className="text-center py-2">
                            <span className="px-4 py-2 bg-green-100 text-green-800 rounded-lg text-sm font-semibold">
                              ✓ Order Completed
                            </span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
              </div>
            )}
          </div>
        )}

        {/* Menu Tab */}
        {activeTab === 'menu' && (
          <>
            <div className="bg-white rounded-xl shadow-sm border border-gray-100">
              <div className="p-3 sm:p-4 lg:p-6 border-b border-gray-200 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <h2 className="text-lg sm:text-xl font-bold text-gray-900">Menu Items</h2>
                <button
                  onClick={handleAddProduct}
                  className="flex items-center px-3 sm:px-4 py-2 text-sm sm:text-base bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 font-medium transition-all duration-200 transform hover:scale-105 shadow-md w-full sm:w-auto justify-center"
                >
                  <svg className="h-4 w-4 sm:h-5 sm:w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                  Add Product
                </button>
              </div>
              {menu.length === 0 ? (
                <div className="p-12 text-center">
                  <svg className="mx-auto h-12 w-12 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                  <p className="text-gray-500 text-lg">No menu items</p>
                  <p className="text-gray-400 text-sm mt-1">Click "Add Product" to get started</p>
                </div>
              ) : (
                <div className="divide-y divide-gray-200">
                  {menu.map((product) => (
                    <div key={product.id} className="p-4 sm:p-5 lg:p-6 hover:bg-gray-50 transition-colors duration-150">
                      <div className="flex flex-col sm:flex-row justify-between items-start gap-4">
                        <div className="flex-1 w-full">
                          <div className="flex items-center gap-2 sm:gap-3 mb-2 flex-wrap">
                            <h3 className="text-base sm:text-lg font-bold text-gray-900">{product.name}</h3>
                            <button
                              onClick={() => handleToggleAvailability(product)}
                              className={`px-3 py-1.5 text-xs font-bold rounded-full shadow-sm transition-all duration-200 hover:shadow-md cursor-pointer ${
                                product.is_available 
                                  ? 'bg-gradient-to-r from-green-100 to-green-200 text-green-800 border border-green-300 hover:from-green-200 hover:to-green-300' 
                                  : 'bg-gradient-to-r from-red-100 to-red-200 text-red-800 border border-red-300 hover:from-red-200 hover:to-red-300'
                              }`}
                              title={product.is_available ? 'Click to mark as unavailable' : 'Click to mark as available'}
                            >
                              {product.is_available ? '✓ Available' : '✕ Unavailable'}
                            </button>
                            <span className="px-3 py-1.5 text-xs font-semibold text-gray-700 bg-gray-100 rounded-lg border border-gray-200">
                              {product.category}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-3 leading-relaxed">{product.description}</p>
                        </div>
                        <div className="w-full sm:w-auto flex flex-col sm:flex-row items-stretch sm:items-center gap-3 sm:gap-4">
                          <div className="bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-xl px-4 sm:px-5 py-2.5 sm:py-3 shadow-lg text-center sm:text-left">
                            <div className="text-xl sm:text-2xl font-bold">₹{product.price.toFixed(2)}</div>
                          </div>
                          <div className="flex gap-2 sm:flex-col lg:flex-row">
                            <button
                              onClick={() => handleEditProduct(product)}
                              className="flex-1 sm:flex-none px-3 sm:px-4 py-2.5 text-xs sm:text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 font-semibold transition-all duration-200 shadow-sm hover:shadow-md"
                            >
                              ✏️ Edit
                            </button>
                            <button
                              onClick={() => handleDeleteProduct(product.id, product.name)}
                              className="flex-1 sm:flex-none px-3 sm:px-4 py-2.5 text-xs sm:text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 font-semibold transition-all duration-200 shadow-sm hover:shadow-md"
                            >
                              🗑️ Delete
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Product Modal */}
            {showProductModal && (
              <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-0 sm:p-4" onClick={() => setShowProductModal(false)}>
                <div className="bg-white rounded-none sm:rounded-2xl shadow-2xl max-w-md w-full h-full sm:h-auto sm:max-h-[90vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
                  <div className="p-4 sm:p-6 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50 sticky top-0 bg-inherit z-10">
                    <h3 className="text-lg sm:text-xl font-bold text-gray-900">
                      {editingProduct ? 'Edit Product' : 'Add New Product'}
                    </h3>
                  </div>
                  <form onSubmit={handleSaveProduct} className="p-4 sm:p-6 space-y-4 sm:space-y-5">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Product Name *
                      </label>
                      <input
                        type="text"
                        required
                        value={productForm.name}
                        onChange={(e) => setProductForm({ ...productForm, name: e.target.value })}
                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200"
                        placeholder="e.g., Butter Chicken"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Description *
                      </label>
                      <textarea
                        required
                        value={productForm.description}
                        onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
                        rows={3}
                        className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 resize-none"
                        placeholder="Product description"
                      />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Price (₹) *
                        </label>
                        <input
                          type="number"
                          required
                          step="0.01"
                          min="0"
                          value={productForm.price}
                          onChange={(e) => setProductForm({ ...productForm, price: e.target.value })}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200"
                          placeholder="0.00"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Category *
                        </label>
                        <input
                          type="text"
                          required
                          value={productForm.category}
                          onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}
                          className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200"
                          placeholder="e.g., Main Course"
                        />
                      </div>
                    </div>
                    <div className="flex items-center p-4 bg-gray-50 rounded-xl">
                      <input
                        type="checkbox"
                        id="available"
                        checked={productForm.is_available}
                        onChange={(e) => setProductForm({ ...productForm, is_available: e.target.checked })}
                        className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                      />
                      <label htmlFor="available" className="ml-3 text-sm font-medium text-gray-700">
                        Product is available
                      </label>
                    </div>
                    <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 pt-4 sticky bottom-0 bg-white pb-2 sm:pb-0">
                      <button
                        type="submit"
                        className="w-full sm:flex-1 px-4 py-2.5 sm:py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 text-sm sm:text-base font-semibold transition-all duration-200 shadow-md"
                      >
                        {editingProduct ? 'Update Product' : 'Add Product'}
                      </button>
                      <button
                        type="button"
                        onClick={() => setShowProductModal(false)}
                        className="w-full sm:flex-1 px-4 py-2.5 sm:py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 text-sm sm:text-base font-semibold transition-colors duration-200"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              </div>
            )}
          </>
        )}

        {/* UPI Management Modal */}
        {showUPIModal && restaurantInfo && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setShowUPIModal(false)}>
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 sm:p-8" onClick={(e) => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Manage UPI Payment</h2>
                <button
                  onClick={() => setShowUPIModal(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <form onSubmit={handleUpdateUPI} className="space-y-4">
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    UPI ID / UPI Number
                  </label>
                  <input
                    type="text"
                    value={upiForm.upi_id}
                    onChange={(e) => setUpiForm({ ...upiForm, upi_id: e.target.value })}
                    placeholder="e.g., restaurant@paytm or 1234567890@upi"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200 font-mono text-sm"
                    required
                  />
                  <div className="text-xs text-gray-600 mt-2 space-y-1">
                    <p className="font-semibold">Valid UPI formats:</p>
                    <ul className="list-disc list-inside space-y-0.5 ml-2">
                      <li>username@paytm (e.g., restaurant@paytm)</li>
                      <li>phone@upi (e.g., 1234567890@upi)</li>
                      <li>username@bank (e.g., restaurant@ybl)</li>
                    </ul>
                    <p className="text-gray-500 mt-2">This UPI ID will be verified and used to receive payments from customers</p>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Password (Owner Only)
                  </label>
                  <input
                    type="password"
                    value={upiForm.password}
                    onChange={(e) => setUpiForm({ ...upiForm, password: e.target.value })}
                    placeholder="Enter your password to verify"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-200"
                    required
                  />
                  <p className="text-xs text-yellow-600 mt-1">⚠️ Only restaurant owner can update UPI details. Password required for security.</p>
                </div>
                
                {restaurantInfo.upi_id && (
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                    <p className="text-sm text-blue-900">
                      <span className="font-semibold">Current UPI:</span> {restaurantInfo.upi_id || 'Not set'}
                    </p>
                  </div>
                )}
                
                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl hover:from-blue-700 hover:to-indigo-700 font-semibold transition-all duration-200 shadow-md"
                  >
                    Verify & Update UPI
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowUPIModal(false);
                      setUpiForm({ upi_id: '', password: '' });
                    }}
                    className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 font-semibold transition-colors duration-200"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Payment Verification Modal */}
        {showPaymentVerify && selectedOrder && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setShowPaymentVerify(false)}>
            <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 sm:p-8" onClick={(e) => e.stopPropagation()}>
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Verify Payment</h2>
                <button
                  onClick={() => setShowPaymentVerify(false)}
                  className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  <svg className="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-900 mb-2">
                    <span className="font-semibold">Order ID:</span> #{selectedOrder.id.slice(-6).toUpperCase()}
                  </p>
                  <p className="text-sm text-blue-900">
                    <span className="font-semibold">Amount:</span> ₹{selectedOrder.total.toFixed(2)}
                  </p>
                  {restaurantInfo?.upi_id && (
                    <p className="text-xs text-blue-700 mt-2">
                      Expected UPI: <span className="font-semibold">{restaurantInfo.upi_id}</span>
                    </p>
                  )}
                </div>
                
                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Customer UPI Name
                  </label>
                  <input
                    type="text"
                    value={paymentUpiName}
                    onChange={(e) => setPaymentUpiName(e.target.value)}
                    placeholder="Enter the UPI name shown in payment notification"
                    className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-green-500 focus:border-green-500 transition duration-200"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">Enter the name shown in your UPI payment notification from the customer</p>
                </div>
                
                <div className="flex gap-3 pt-4">
                  <button
                    onClick={handleVerifyPayment}
                    className="flex-1 px-4 py-3 bg-gradient-to-r from-green-600 to-green-700 text-white rounded-xl hover:from-green-700 hover:to-green-800 font-semibold transition-all duration-200 shadow-md"
                  >
                    ✓ Verify Payment
                  </button>
                  <button
                    onClick={() => setShowPaymentVerify(false)}
                    className="flex-1 px-4 py-3 bg-gray-200 text-gray-700 rounded-xl hover:bg-gray-300 font-semibold transition-colors duration-200"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* QR Code Modal - Full Screen for Better Visibility */}
        {showQRCode && restaurantInfo && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4" onClick={() => setShowQRCode(false)}>
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[95vh] overflow-y-auto" onClick={(e) => e.stopPropagation()}>
              <div className="text-center p-6 sm:p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl sm:text-3xl font-bold text-gray-900">WhatsApp Ordering QR Code</h2>
                  <button
                    onClick={() => setShowQRCode(false)}
                    className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    <svg className="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
                
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 sm:p-8 mb-6">
                  <p className="text-xl sm:text-2xl font-bold text-gray-900 mb-2">{restaurantInfo.name}</p>
                  <p className="text-sm sm:text-base text-gray-600 mb-6">{restaurantInfo.phone}</p>
                  
                  {/* Large QR Code - Dynamic WhatsApp URL with resto_restaurant_id format */}
                  <div className="bg-white p-6 sm:p-8 rounded-xl shadow-2xl inline-block mb-6">
                    <img
                      src={`https://api.qrserver.com/v1/create-qr-code/?size=600x600&margin=3&data=${encodeURIComponent(`https://wa.me/${restaurantInfo.twilio_number || '14155238886'}?text=resto_${restaurantInfo.id}`)}`}
                      alt="WhatsApp QR Code"
                      className="w-full max-w-[450px] sm:max-w-[550px] h-auto mx-auto border-4 border-gray-200"
                      style={{ minWidth: '350px', minHeight: '350px' }}
                    />
                  </div>
                  
                  <div className="mt-6 space-y-2">
                    <p className="text-base sm:text-lg font-semibold text-gray-900">📱 Scan to order from {restaurantInfo.name}</p>
                    <div className="bg-white rounded-lg p-4 inline-block">
                      <p className="text-sm text-gray-600">Restaurant ID:</p>
                      <p className="text-lg font-mono font-bold text-blue-600 mt-1">{restaurantInfo.id}</p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-green-50 border-2 border-green-300 rounded-xl p-4 sm:p-6 mb-6">
                  <div className="flex items-center justify-center gap-2 mb-3">
                    <svg className="h-6 w-6 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                    </svg>
                    <p className="text-green-800 font-bold text-lg">How to Use This QR Code</p>
                  </div>
                  <div className="text-left space-y-2 text-sm sm:text-base text-green-700">
                    <p>1. <strong>Print or Display:</strong> Show this QR code at your restaurant</p>
                    <p>2. <strong>Customer Scans:</strong> Customer scans with WhatsApp camera</p>
                    <p>3. <strong>Auto-Identifies:</strong> Restaurant ID ({restaurantInfo.id}) is sent automatically</p>
                    <p>4. <strong>Menu Appears:</strong> Customer receives menu and can start ordering</p>
                  </div>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-3 justify-center mb-6">
                  <a
                    href={`https://wa.me/${restaurantInfo.twilio_number || '14155238886'}?text=resto_${restaurantInfo.id}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-green-500 hover:bg-green-600 text-white rounded-lg font-semibold transition-colors shadow-md text-base"
                  >
                    <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                    </svg>
                    Test on WhatsApp
                  </a>
                  <button
                    onClick={() => {
                      const twilioNum = restaurantInfo.twilio_number || '14155238886';
                      const qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=600x600&margin=3&data=${encodeURIComponent(`https://wa.me/${twilioNum}?text=resto_${restaurantInfo.id}`)}`;
                      const link = document.createElement('a');
                      link.href = qrUrl;
                      link.download = `qr-code-${restaurantInfo.id}.png`;
                      link.click();
                    }}
                    className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-semibold transition-colors shadow-md text-base"
                  >
                    <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                    </svg>
                    Download QR Code
                  </button>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4 text-left">
                  <p className="font-semibold mb-2 text-gray-900">ℹ️ Technical Details:</p>
                  <ul className="text-sm text-gray-600 space-y-1 list-disc list-inside">
                    <li>QR code format: <code className="bg-gray-200 px-1 rounded">https://wa.me/{restaurantInfo.twilio_number || '14155238886'}?text=resto_{restaurantInfo.id}</code></li>
                    <li>Twilio WhatsApp number: <code className="bg-gray-200 px-1 rounded">+{restaurantInfo.twilio_number || '14155238886'}</code></li>
                    <li>Restaurant ID: <code className="bg-gray-200 px-1 rounded">{restaurantInfo.id}</code></li>
                    <li>Message sent: <code className="bg-gray-200 px-1 rounded">resto_{restaurantInfo.id}</code></li>
                    <li>Backend extracts restaurant ID and sends menu automatically</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
