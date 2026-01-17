'use client';

import { useEffect, useState, useRef } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { apiClient } from '@/lib/api';

export default function PaymentPage() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const orderId = searchParams.get('order_id');
  
  const [order, setOrder] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [paymentStatus, setPaymentStatus] = useState<'pending' | 'verifying' | 'verified' | 'failed'>('pending');
  const [qrCode, setQrCode] = useState<string | null>(null);
  const [upiName, setUpiName] = useState('');
  const [amountPaid, setAmountPaid] = useState('');
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const pollingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (orderId) {
      loadOrder();
    } else {
      // Try to get from sessionStorage
      const pendingOrder = sessionStorage.getItem('pendingOrder');
      if (pendingOrder) {
        const orderData = JSON.parse(pendingOrder);
        setOrder(orderData);
        setLoading(false);
      } else {
        setError('Order not found');
        setLoading(false);
      }
    }

    // Cleanup polling on unmount
    return () => {
      if (pollingIntervalRef.current) {
        clearInterval(pollingIntervalRef.current);
      }
    };
  }, [orderId]);

  const loadOrder = async () => {
    try {
      // Get order from sessionStorage
      const pendingOrder = sessionStorage.getItem('pendingOrder');
      if (pendingOrder) {
        const orderData = JSON.parse(pendingOrder);
        setOrder(orderData);
        
        // Fetch restaurant info to get QR code using public endpoint (no auth required)
        try {
          if (orderData.restaurant_id) {
            const menuData = await apiClient.getPublicMenu(orderData.restaurant_id);
            if (menuData.restaurant.upi_qr_code) {
              setQrCode(menuData.restaurant.upi_qr_code);
            }
          }
        } catch (err) {
          console.warn('Failed to load QR code:', err);
          // Continue without QR code - payment link will still work
        }

        // If Razorpay payment link ID exists, start polling
        if (orderData.razorpay_payment_link_id) {
          startPaymentPolling(orderData.razorpay_payment_link_id);
        }
      }
      setLoading(false);
    } catch (err) {
      setError('Failed to load order');
      setLoading(false);
    }
  };

  const startPaymentPolling = (paymentLinkId: string) => {
    // Poll every 3 seconds for payment status
    pollingIntervalRef.current = setInterval(async () => {
      try {
        const status = await apiClient.getPaymentStatus(paymentLinkId);
        
        if (status.status === 'paid') {
          // Payment successful!
          setPaymentStatus('verified');
          
          // Stop polling
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
          
          // Clear session storage
          sessionStorage.removeItem('pendingOrder');
          
          // Redirect after showing success message
          setTimeout(() => {
            router.push('/');
          }, 3000);
        } else if (status.status === 'cancelled') {
          // Payment cancelled
          setPaymentStatus('failed');
          
          // Stop polling
          if (pollingIntervalRef.current) {
            clearInterval(pollingIntervalRef.current);
            pollingIntervalRef.current = null;
          }
        }
        // Continue polling if status is 'created' or 'pending'
      } catch (err) {
        console.error('Error polling payment status:', err);
        // Continue polling on error
      }
    }, 3000); // Poll every 3 seconds
  };

  const handlePaymentClick = () => {
    if (order?.payment_link) {
      // Open payment link in new tab
      window.open(order.payment_link, '_blank');
      // Show payment form after clicking pay (customer can fill after payment)
      setShowPaymentForm(true);
    }
  };

  // Show payment form when QR code is displayed (customer can fill after scanning)
  useEffect(() => {
    if (qrCode && !order?.razorpay_payment_link_id) {
      // Show form after a short delay to let customer scan QR first
      const timer = setTimeout(() => {
        setShowPaymentForm(true);
      }, 2000);
      return () => clearTimeout(timer);
    }
  }, [qrCode, order?.razorpay_payment_link_id]);

  const handleSubmitPaymentDetails = async () => {
    const currentOrderId = orderId || order?.orderId || order?.id;
    if (!currentOrderId || !upiName || !amountPaid) {
      alert('Please fill in all fields');
      return;
    }

    const paidAmount = parseFloat(amountPaid);
    if (isNaN(paidAmount) || paidAmount <= 0) {
      alert('Please enter a valid amount');
      return;
    }

    try {
      setPaymentStatus('verifying');
      
      // Call public payment verification endpoint to save payment details
      const result = await apiClient.verifyPaymentPublic(currentOrderId, upiName, paidAmount);

      if (result.success) {
        setPaymentStatus('verified');
        
        // Clear session storage
        sessionStorage.removeItem('pendingOrder');
        
        // Show success message briefly, then redirect
        setTimeout(() => {
          router.push('/');
        }, 3000);
      } else {
        setPaymentStatus('failed');
        alert(`❌ ${result.message}\n\nYour order has been cancelled and refund will be processed.`);
        
        // Clear session storage
        sessionStorage.removeItem('pendingOrder');
        
        // Redirect after a delay
        setTimeout(() => {
          router.push('/');
        }, 3000);
      }
    } catch (err: any) {
      setPaymentStatus('failed');
      const errorMessage = err.message || 'Failed to submit payment details. Please contact support.';
      alert(`❌ ${errorMessage}`);
      console.error('Payment submission error:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading payment details...</p>
        </div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="text-6xl mb-4">❌</div>
          <h1 className="text-2xl font-bold text-gray-800 mb-2">Order Not Found</h1>
          <p className="text-gray-600 mb-6">{error || 'Unable to load order details'}</p>
          <button
            onClick={() => router.push('/')}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
          >
            Go Home
          </button>
        </div>
      </div>
    );
  }

  // If payment is verified, show success message
  if (paymentStatus === 'verified') {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-md w-full text-center">
          <div className="text-6xl mb-4">✅</div>
          <h1 className="text-2xl font-bold text-green-600 mb-2">Payment Successful!</h1>
          <p className="text-gray-600 mb-4">
            Your payment of ₹{order.totalAmount || order.total_amount || order.total} has been confirmed.
          </p>
          <p className="text-sm text-gray-500 mb-6">
            Your order is now being processed. You'll receive a confirmation on WhatsApp shortly.
          </p>
          <p className="text-xs text-gray-400">Redirecting to home page...</p>
        </div>
      </div>
    );
  }

  // Main payment page
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl w-full">
        <div className="text-center mb-6">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">Complete Your Payment</h1>
          <p className="text-gray-600">Order #{order.orderId || order.id?.slice(0, 8)}</p>
        </div>

        <div className="bg-purple-50 rounded-xl p-6 mb-6">
          <div className="flex justify-between items-center mb-2">
            <span className="text-gray-700 font-medium">Total Amount:</span>
            <span className="text-2xl font-bold text-purple-600">
              ₹{order.totalAmount || order.total_amount || order.total}
            </span>
          </div>
        </div>

        {/* QR Code Payment (Primary Method) */}
        {qrCode && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold text-gray-800 mb-3 text-center">
              Scan QR Code to Pay
            </h2>
            <div className="flex justify-center mb-4">
              <div className="bg-white p-4 rounded-lg shadow-lg border-2 border-purple-200">
                <img
                  src={qrCode}
                  alt="UPI QR Code"
                  className="w-64 h-64 object-contain"
                />
              </div>
            </div>
            <p className="text-sm text-gray-600 text-center mb-4">
              Scan this QR code with any UPI app (PhonePe, GPay, Paytm, etc.)
            </p>
          </div>
        )}

        {/* Payment Link (Alternative Method) */}
        {order.payment_link && (
          <div className="mb-6">
            <div className="text-center">
              <p className="text-sm text-gray-600 mb-3">Or click to pay directly:</p>
              <button
                onClick={handlePaymentClick}
                className="bg-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors shadow-lg"
              >
                Pay Now
              </button>
            </div>
          </div>
        )}

        {/* Payment Details Form - Show after customer pays */}
        {showPaymentForm && !order.razorpay_payment_link_id && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-4 text-center">
              ✅ Payment Details
            </h3>
            <p className="text-sm text-gray-600 mb-4 text-center">
              After making payment, please enter your payment details below:
            </p>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your UPI Name / Number *
                </label>
                <input
                  type="text"
                  value={upiName}
                  onChange={(e) => setUpiName(e.target.value)}
                  placeholder="e.g., John Doe or 9876543210"
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter the name or number shown in your UPI app after payment
                </p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Amount Paid (₹) *
                </label>
                <input
                  type="number"
                  value={amountPaid}
                  onChange={(e) => setAmountPaid(e.target.value)}
                  placeholder={`₹${order.totalAmount || order.total_amount || order.total}`}
                  className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Expected: ₹{order.totalAmount || order.total_amount || order.total}
                </p>
              </div>
              <button
                onClick={handleSubmitPaymentDetails}
                disabled={paymentStatus === 'verifying' || paymentStatus === 'verified' || !upiName || !amountPaid}
                className="w-full bg-purple-600 text-white py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {paymentStatus === 'verifying' ? 'Submitting...' : paymentStatus === 'verified' ? 'Submitted ✓' : 'Submit Payment Details'}
              </button>
            </div>
          </div>
        )}

        {/* Payment Status Indicator for Razorpay */}
        {order.razorpay_payment_link_id && (
          <div className="mt-6 text-center">
            <div className="inline-flex items-center gap-2 text-sm text-gray-600">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-purple-600"></div>
              <span>Waiting for payment confirmation...</span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              This page will automatically update when payment is received
            </p>
          </div>
        )}

        {/* Instructions */}
        {!showPaymentForm && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Payment Instructions:</h3>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• Scan the QR code or click "Pay Now" to complete payment</li>
              <li>• Ensure you pay the exact amount: ₹{order.totalAmount || order.total_amount || order.total}</li>
              <li>• After payment, you'll be asked to enter your payment details</li>
              <li>• Restaurant will verify and you'll receive confirmation on WhatsApp</li>
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
