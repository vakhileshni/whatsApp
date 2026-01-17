'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiClient, RestaurantInfo } from '@/lib/api';

interface NotificationSettings {
  whatsapp_enabled: boolean;
  whatsapp_number: string;
  email_enabled: boolean;
  email_address: string;
  sms_enabled: boolean;
  sms_number: string;
  notify_new_order: boolean;
  notify_preparing: boolean;
  notify_ready: boolean;
  notify_delivered: boolean;
  notify_cancelled: boolean;
  notify_payment: boolean;
  sound_enabled: boolean;
  blink_enabled: boolean;
}

interface SubscriptionInfo {
  plan_name: string;
  plan_type: 'free' | 'basic' | 'pro' | 'enterprise';
  status: 'active' | 'expired' | 'trial' | 'cancelled';
  start_date: string;
  expiry_date: string;
  billing_cycle: 'monthly' | 'annual';
  auto_renewal: boolean;
}

interface Plan {
  id: string;
  name: string;
  type: 'free' | 'basic' | 'pro' | 'enterprise';
  price_monthly: number;
  price_annual: number;
  features: string[];
  order_limit: number | null; // null = unlimited
}

interface PaymentRecord {
  id: string;
  date: string;
  amount: number;
  plan_name: string;
  status: 'success' | 'failed' | 'pending';
  transaction_id: string;
  invoice_url?: string;
}

interface ProfileSettings {
  restaurant_name: string;
  phone: string;
  email: string;
  address: string;
  latitude: number;
  longitude: number;
  delivery_radius: number;
  operating_hours: {
    [key: string]: { open: string; close: string; closed: boolean };
  };
  gst_number: string;
  pan_number: string;
  fssai_number: string;
}

interface AccountSettings {
  owner_name: string;
  owner_email: string;
  owner_phone: string;
  current_password: string;
  new_password: string;
  confirm_password: string;
  two_factor_enabled: boolean;
}

interface OrderSettings {
  delivery_available: boolean;
  auto_accept_orders: boolean;
  default_preparation_time: number; // minutes
  minimum_order_value: number;
  maximum_order_value: number | null;
  allow_order_modifications: boolean;
  cancellation_policy: string;
}

export default function SettingsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'notifications' | 'subscription' | 'payments' | 'profile' | 'account' | 'orders' | 'support'>('notifications');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [restaurantInfo, setRestaurantInfo] = useState<RestaurantInfo | null>(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);
  const [showPaymentHistory, setShowPaymentHistory] = useState(false);
  const [billingCycle, setBillingCycle] = useState<'monthly' | 'annual'>('monthly');
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null);
  const [paymentMethod, setPaymentMethod] = useState<'card' | 'upi' | 'wallet' | 'netbanking'>('card');
  const [processingPayment, setProcessingPayment] = useState(false);
  
  // Card payment form state
  const [cardDetails, setCardDetails] = useState({
    cardNumber: '',
    cardHolder: '',
    expiryDate: '',
    cvv: '',
  });

  // UPI payment form state
  const [upiId, setUpiId] = useState('');
  
  // UPI QR code management state
  const [upiQrCode, setUpiQrCode] = useState('');
  const [qrCodeFile, setQrCodeFile] = useState<File | null>(null);
  const [savingQrCode, setSavingQrCode] = useState(false);
  const [showQrCodeModal, setShowQrCodeModal] = useState(false);

  // Wallet selection
  const [selectedWallet, setSelectedWallet] = useState<'paytm' | 'phonepe' | 'gpay' | null>(null);

  // Net Banking selection
  const [selectedBank, setSelectedBank] = useState<string>('');
  
  const [notificationSettings, setNotificationSettings] = useState<NotificationSettings>({
    whatsapp_enabled: true,
    whatsapp_number: '',
    email_enabled: false,
    email_address: '',
    sms_enabled: false,
    sms_number: '',
    notify_new_order: true,
    notify_preparing: true,
    notify_ready: true,
    notify_delivered: true,
    notify_cancelled: true,
    notify_payment: true,
    sound_enabled: true,
    blink_enabled: true,
  });

  const [subscriptionInfo, setSubscriptionInfo] = useState<SubscriptionInfo>({
    plan_name: 'Free Plan',
    plan_type: 'free',
    status: 'active',
    start_date: new Date().toISOString(),
    expiry_date: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString(),
    billing_cycle: 'monthly',
    auto_renewal: false,
  });

  const [plans] = useState<Plan[]>([
    {
      id: 'free',
      name: 'Free Plan',
      type: 'free',
      price_monthly: 0,
      price_annual: 0,
      order_limit: 50,
      features: [
        'Up to 50 orders/month',
        'Basic menu management',
        'WhatsApp notifications',
        'Email support',
        'Basic dashboard'
      ]
    },
    {
      id: 'basic',
      name: 'Basic Plan',
      type: 'basic',
      price_monthly: 200,
      price_annual: 2000,
      order_limit: 500,
      features: [
        'Up to 500 orders/month',
        'Full menu management',
        'All notification types',
        'Basic analytics',
        'Email & WhatsApp support',
        'Discount management'
      ]
    },
    {
      id: 'pro',
      name: 'Pro Plan',
      type: 'pro',
      price_monthly: 250,
      price_annual: 2500,
      order_limit: null,
      features: [
        'Unlimited orders',
        'Advanced analytics',
        'Priority support',
        'API access',
        'Custom integrations',
        'Advanced reporting',
        'Multi-location support'
      ]
    },
    {
      id: 'enterprise',
      name: 'Enterprise Plan',
      type: 'enterprise',
      price_monthly: 350,
      price_annual: 3500,
      order_limit: null,
      features: [
        'Unlimited everything',
        'Dedicated account manager',
        'Custom features',
        'SLA guarantee',
        '24/7 phone support',
        'White-label options',
        'Advanced security'
      ]
    }
  ]);

  const [paymentHistory] = useState<PaymentRecord[]>([
    {
      id: 'pay_001',
      date: new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      amount: 0,
      plan_name: 'Free Plan',
      status: 'success',
      transaction_id: 'TXN_FREE_001'
    }
  ]);

  const [profileSettings, setProfileSettings] = useState<ProfileSettings>({
    restaurant_name: '',
    phone: '',
    email: '',
    address: '',
    latitude: 0,
    longitude: 0,
    delivery_radius: 10,
    operating_hours: {
      monday: { open: '09:00', close: '22:00', closed: false },
      tuesday: { open: '09:00', close: '22:00', closed: false },
      wednesday: { open: '09:00', close: '22:00', closed: false },
      thursday: { open: '09:00', close: '22:00', closed: false },
      friday: { open: '09:00', close: '22:00', closed: false },
      saturday: { open: '09:00', close: '22:00', closed: false },
      sunday: { open: '09:00', close: '22:00', closed: false },
    },
    gst_number: '',
    pan_number: '',
    fssai_number: ''
  });

  const [accountSettings, setAccountSettings] = useState<AccountSettings>({
    owner_name: '',
    owner_email: '',
    owner_phone: '',
    current_password: '',
    new_password: '',
    confirm_password: '',
    two_factor_enabled: false
  });

  const [orderSettings, setOrderSettings] = useState<OrderSettings>({
    delivery_available: true,
    auto_accept_orders: false,
    default_preparation_time: 30,
    minimum_order_value: 0,
    maximum_order_value: null,
    allow_order_modifications: true,
    cancellation_policy: 'Orders can be cancelled within 5 minutes of placing. After that, contact restaurant directly.'
  });

  useEffect(() => {
    if (!apiClient.isAuthenticated()) {
      router.push('/login');
      return;
    }
    
    // Only load once on mount
    loadSettings();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency array - only run on mount

  const loadSettings = async () => {
    try {
      setLoading(true);
      
      // Add timeout to prevent infinite loading
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout - backend may not be responding')), 10000)
      );
      
      const infoPromise = apiClient.getRestaurantInfo();
      const info = await Promise.race([infoPromise, timeoutPromise]) as any;
      
      setRestaurantInfo(info);
      
      // Load UPI QR code
      if (info.upi_qr_code && info.upi_qr_code.trim().length > 0) {
        setUpiQrCode(info.upi_qr_code);
        console.log('✅ Loaded QR code from database:', {
          length: info.upi_qr_code.length,
          type: info.upi_qr_code.substring(0, 30) + '...',
          startsWith: info.upi_qr_code.substring(0, 20)
        });
      } else {
        setUpiQrCode(''); // Clear if empty
        console.log('ℹ️ No QR code found in database for restaurant:', info.id);
      }
      
      // Load settings from database
      try {
        const settingsData = await apiClient.getSettings();
        setNotificationSettings({
          whatsapp_enabled: settingsData.whatsapp_notifications_enabled,
          whatsapp_number: settingsData.whatsapp_number || info.phone || '',
          email_enabled: settingsData.email_notifications_enabled,
          email_address: settingsData.email_address || '',
          sms_enabled: settingsData.sms_notifications_enabled,
          sms_number: settingsData.sms_number || '',
          notify_new_order: settingsData.notify_new_order,
          notify_preparing: settingsData.notify_preparing,
          notify_ready: settingsData.notify_ready,
          notify_delivered: settingsData.notify_delivered,
          notify_cancelled: settingsData.notify_cancelled,
          notify_payment: settingsData.notify_payment,
          sound_enabled: settingsData.sound_enabled,
          blink_enabled: settingsData.blink_enabled,
        });
        
        setOrderSettings({
          delivery_available: settingsData.delivery_available !== false,
          auto_accept_orders: settingsData.auto_accept_orders,
          default_preparation_time: settingsData.default_preparation_time,
          minimum_order_value: settingsData.minimum_order_value,
          maximum_order_value: settingsData.maximum_order_value || null,
          allow_order_modifications: settingsData.allow_order_modifications,
          cancellation_policy: settingsData.cancellation_policy || '',
        });

        // Load profile-related settings from settings table (if present)
        setProfileSettings(prev => ({
          ...prev,
          delivery_radius: settingsData.delivery_radius_km ?? prev.delivery_radius,
          gst_number: settingsData.gst_number || prev.gst_number,
          pan_number: settingsData.pan_number || prev.pan_number,
          fssai_number: settingsData.fssai_number || prev.fssai_number,
          // If operating_hours JSON string is present, parse and merge
          ...(settingsData.operating_hours
            ? { operating_hours: { ...prev.operating_hours, ...JSON.parse(settingsData.operating_hours) } }
            : {})
        }));
      } catch (err) {
        console.warn('Failed to load settings from database, using defaults:', err);
        // Set default WhatsApp number from restaurant info
        setNotificationSettings(prev => ({
          ...prev,
          whatsapp_number: info.phone || '',
        }));
      }

      // Load profile settings from restaurant info
      setProfileSettings(prev => ({
        ...prev,
        restaurant_name: info.name || '',
        phone: info.phone || '',
        address: info.address || '',
        latitude: info.latitude || 0,
        longitude: info.longitude || 0,
        // delivery_radius can be calculated or set default
        // operating_hours, gst_number, pan_number, fssai_number need separate storage
      }));

      // Load account (owner) settings from backend
      try {
        const profile = await apiClient.getCurrentUserProfile();
        setAccountSettings(prev => ({
          ...prev,
          owner_name: profile.owner_name || '',
          owner_email: profile.owner_email || '',
          owner_phone: profile.restaurant_phone || info.phone || '',
        }));
        
        // Also set email in profile settings from owner email
        setProfileSettings(prev => ({
          ...prev,
          email: profile.owner_email || '',
        }));
      } catch (e) {
        console.warn('Failed to load account (owner) info, using defaults', e);
      }
      
      // TODO: Load subscription info from API
      // const subInfo = await apiClient.getSubscription();
      // setSubscriptionInfo(subInfo);
      
    } catch (err) {
      console.error('Failed to load settings:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to load settings';
      
      // Always set loading to false even on error
      setLoading(false);
      
      // Show user-friendly error
      if (errorMessage.includes('Failed to connect') || errorMessage.includes('timeout')) {
        const backendUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';
        alert(`⚠️ Cannot connect to backend server!\n\nPlease ensure:\n1. Backend is running at ${backendUrl}\n2. Backend is accessible\n3. No firewall blocking the connection\n\nYou can still use the page, but some features may not work.`);
      } else {
        alert(`⚠️ Error loading settings: ${errorMessage}\n\nThe page will still load, but some data may be missing.`);
      }
    } finally {
      // Ensure loading is always set to false
      setLoading(false);
    }
  };

  const handleSaveNotifications = async () => {
    try {
      setSaving(true);
      
      // Save to backend API
      await apiClient.updateNotificationSettings({
        whatsapp_notifications_enabled: notificationSettings.whatsapp_enabled,
        whatsapp_number: notificationSettings.whatsapp_number || undefined,
        email_notifications_enabled: notificationSettings.email_enabled,
        email_address: notificationSettings.email_address || undefined,
        sms_notifications_enabled: notificationSettings.sms_enabled,
        sms_number: notificationSettings.sms_number || undefined,
        notify_new_order: notificationSettings.notify_new_order,
        notify_preparing: notificationSettings.notify_preparing,
        notify_ready: notificationSettings.notify_ready,
        notify_delivered: notificationSettings.notify_delivered,
        notify_cancelled: notificationSettings.notify_cancelled,
        notify_payment: notificationSettings.notify_payment,
        sound_enabled: notificationSettings.sound_enabled,
        blink_enabled: notificationSettings.blink_enabled,
      });
      
      alert('✅ Notification settings saved successfully to database!');
    } catch (err) {
      console.error('Failed to save notification settings:', err);
      alert('Failed to save notification settings: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleTestNotification = async () => {
    try {
      setSaving(true);
      const response = await apiClient.sendTestNotification();
      alert(`✅ ${response.message}\n\nRecipient: ${response.recipient}`);
    } catch (err: any) {
      console.error('Failed to send test notification:', err);
      const errorMessage = err?.message || 'Failed to send test notification. Please check your WhatsApp number in settings.';
      alert(`❌ ${errorMessage}`);
    } finally {
      setSaving(false);
    }
  };

  const handleUpgradePlan = async (plan: Plan) => {
    try {
      const amount = billingCycle === 'monthly' ? plan.price_monthly : plan.price_annual;
      
      if (amount === 0) {
        alert('You are already on the Free Plan. Please select a paid plan to upgrade.');
        return;
      }

      setSelectedPlan(plan);
      setShowUpgradeModal(true);
      // Reset payment form
      setCardDetails({ cardNumber: '', cardHolder: '', expiryDate: '', cvv: '' });
      setUpiId('');
      setSelectedWallet(null);
      setSelectedBank('');
      setPaymentMethod('card');
    } catch (err) {
      alert('Failed to process upgrade');
    }
  };

  const handlePayment = async () => {
    if (!selectedPlan) return;

    const amount = billingCycle === 'monthly' ? selectedPlan.price_monthly : selectedPlan.price_annual;

    // Validation based on payment method
    if (paymentMethod === 'card') {
      if (!cardDetails.cardNumber || !cardDetails.cardHolder || !cardDetails.expiryDate || !cardDetails.cvv) {
        alert('Please fill all card details');
        return;
      }
      if (cardDetails.cardNumber.replace(/\s/g, '').length !== 16) {
        alert('Please enter a valid 16-digit card number');
        return;
      }
      if (cardDetails.cvv.length !== 3 && cardDetails.cvv.length !== 4) {
        alert('Please enter a valid CVV');
        return;
      }
    } else if (paymentMethod === 'upi') {
      if (!upiId || !upiId.includes('@')) {
        alert('Please enter a valid UPI ID (e.g., yourname@paytm)');
        return;
      }
    } else if (paymentMethod === 'wallet') {
      if (!selectedWallet) {
        alert('Please select a wallet');
        return;
      }
    } else if (paymentMethod === 'netbanking') {
      if (!selectedBank) {
        alert('Please select a bank');
        return;
      }
    }

    try {
      setProcessingPayment(true);
      
      // Simulate payment processing
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // TODO: Integrate with actual payment gateway (Razorpay/Stripe/PayU)
      // For now, simulate successful payment
      const transactionId = 'TXN' + Date.now().toString().slice(-10);
      
      alert(
        `✅ Payment Successful!\n\n` +
        `Plan: ${selectedPlan.name}\n` +
        `Amount: ₹${amount.toLocaleString()}\n` +
        `Transaction ID: ${transactionId}\n\n` +
        `Your subscription will be activated shortly.`
      );

      // Update subscription info
      setSubscriptionInfo(prev => ({
        ...prev,
        plan_name: selectedPlan.name,
        plan_type: selectedPlan.type,
        status: 'active',
        start_date: new Date().toISOString(),
        expiry_date: new Date(Date.now() + (billingCycle === 'monthly' ? 30 : 365) * 24 * 60 * 60 * 1000).toISOString(),
        billing_cycle: billingCycle,
        auto_renewal: true,
      }));

      setShowUpgradeModal(false);
      setSelectedPlan(null);
      
    } catch (error) {
      alert('❌ Payment failed. Please try again.');
    } finally {
      setProcessingPayment(false);
    }
  };

  const formatCardNumber = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    const matches = v.match(/\d{4,16}/g);
    const match = matches && matches[0] || '';
    const parts = [];
    for (let i = 0, len = match.length; i < len; i += 4) {
      parts.push(match.substring(i, i + 4));
    }
    if (parts.length) {
      return parts.join(' ');
    } else {
      return v;
    }
  };

  const formatExpiryDate = (value: string) => {
    const v = value.replace(/\s+/g, '').replace(/[^0-9]/gi, '');
    if (v.length >= 2) {
      return v.substring(0, 2) + '/' + v.substring(2, 4);
    }
    return v;
  };

  const handleSaveProfile = async () => {
    try {
      setSaving(true);
      await apiClient.updateProfileSettings({
        restaurant_name: profileSettings.restaurant_name,
        phone: profileSettings.phone,
        address: profileSettings.address,
        latitude: profileSettings.latitude,
        longitude: profileSettings.longitude,
        delivery_radius_km: profileSettings.delivery_radius,
        gst_number: profileSettings.gst_number || null,
        pan_number: profileSettings.pan_number || null,
        fssai_number: profileSettings.fssai_number || null,
        operating_hours: profileSettings.operating_hours,
      });
      alert('✅ Profile settings saved successfully to database!');
    } catch (err) {
      console.error('Failed to save profile settings:', err);
      alert('Failed to save profile settings: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleQrCodeFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        alert('File size should be less than 5MB');
        return;
      }
      if (!file.type.startsWith('image/')) {
        alert('Please select an image file');
        return;
      }
      setQrCodeFile(file);
      const reader = new FileReader();
      reader.onloadend = () => {
        const base64 = reader.result as string;
        setUpiQrCode(base64);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleGenerateQrCode = () => {
    if (!restaurantInfo?.upi_id) {
      alert('Please set UPI ID first');
      return;
    }
    // Generate QR code from UPI ID
    const qrData = `upi://pay?pa=${encodeURIComponent(restaurantInfo.upi_id)}&pn=${encodeURIComponent(restaurantInfo.name)}&am=&cu=INR`;
    const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=400x400&margin=2&data=${encodeURIComponent(qrData)}`;
    setUpiQrCode(qrCodeUrl);
  };

  const handleSaveQrCode = async () => {
    if (!upiQrCode) {
      alert('Please upload or generate a QR code');
      return;
    }

    // Validate QR code format
    if (!upiQrCode.startsWith('data:image/') && !upiQrCode.startsWith('http://') && !upiQrCode.startsWith('https://')) {
      alert('Invalid QR code format. Please upload an image file or generate a QR code.');
      return;
    }

    try {
      setSavingQrCode(true);
      console.log('Saving QR code to database...', {
        length: upiQrCode.length,
        type: upiQrCode.substring(0, 50) + '...',
        isBase64: upiQrCode.startsWith('data:image/')
      });
      
      const updated = await apiClient.saveUPIQRCode(upiQrCode);
      
      console.log('✅ QR code save response:', {
        upi_id: updated?.upi_id,
        has_qr_code: !!updated?.upi_qr_code,
        qr_length: updated?.upi_qr_code?.length
      });
      
      // Verify it was saved
      if (updated && updated.upi_qr_code && updated.upi_qr_code.length > 0) {
        // Update state immediately
        setRestaurantInfo(updated);
        setUpiQrCode(updated.upi_qr_code);
        
        // Check if UPI ID was extracted
        if (updated.upi_id && updated.upi_id.trim().length > 0) {
          console.log('✅ UPI ID automatically extracted:', updated.upi_id);
          alert(`✅ QR code saved successfully!\n\n✅ UPI ID automatically extracted: ${updated.upi_id}`);
        } else {
          console.warn('⚠️ UPI ID was not extracted from QR code');
          alert('✅ QR code saved successfully!\n\n⚠️ Note: UPI ID was not automatically extracted. Please check backend logs or manually set UPI ID.');
        }
        
        // Verify it matches (compare first 100 chars for base64)
        const sentPreview = upiQrCode.substring(0, Math.min(100, upiQrCode.length));
        const receivedPreview = updated.upi_qr_code.substring(0, Math.min(100, updated.upi_qr_code.length));
        
        if (sentPreview === receivedPreview || updated.upi_qr_code === upiQrCode) {
          console.log('QR code saved successfully', {
            length: updated.upi_qr_code.length,
            preview: updated.upi_qr_code.substring(0, 50),
            upi_id: updated.upi_id
          });
        } else {
          console.warn('QR code preview mismatch (but saved)', {
            sentLength: upiQrCode.length,
            receivedLength: updated.upi_qr_code.length
          });
        }
        
        // Refresh restaurant info to ensure UPI ID is loaded
        try {
          const refreshedInfo = await apiClient.getRestaurantInfo();
          console.log('🔄 Refreshed restaurant info:', {
            upi_id: refreshedInfo.upi_id,
            has_qr: !!refreshedInfo.upi_qr_code
          });
          setRestaurantInfo(refreshedInfo);
        } catch (refreshErr) {
          console.warn('Failed to refresh restaurant info:', refreshErr);
        }
      } else {
        console.error('QR code not returned from server', updated);
        alert('⚠️ Error: QR code may not have been saved. Please check console and try again.');
      }
    } catch (err) {
      console.error('Error saving QR code:', err);
      const errorMessage = err instanceof Error ? err.message : 'Failed to save QR code';
      alert(`❌ Error: ${errorMessage}\n\nPlease check:\n1. Backend server is running\n2. You are logged in\n3. Network connection is stable`);
    } finally {
      setSavingQrCode(false);
    }
  };

  const handleSaveAccount = async () => {
    try {
      // Validate password fields if changing password
      if (accountSettings.new_password) {
        if (accountSettings.new_password !== accountSettings.confirm_password) {
          alert('New password and confirm password do not match');
          return;
        }

        if (accountSettings.new_password.length < 6) {
          alert('New password must be at least 6 characters');
          return;
        }

        if (!accountSettings.current_password) {
          alert('Current password is required to change password');
          return;
        }
      }

      setSaving(true);
      
      // Prepare request data
      const updateData: {
        owner_name: string;
        owner_email: string;
        current_password?: string;
        new_password?: string;
        two_factor_enabled: boolean;
      } = {
        owner_name: accountSettings.owner_name,
        owner_email: accountSettings.owner_email,
        two_factor_enabled: accountSettings.two_factor_enabled,
      };

      // Only include password fields if changing password
      if (accountSettings.new_password) {
        updateData.current_password = accountSettings.current_password;
        updateData.new_password = accountSettings.new_password;
      }

      // Call backend API
      await apiClient.updateAccountSettings(updateData);
      
      alert('✅ Account settings saved successfully!');
      
      // Clear password fields
      setAccountSettings(prev => ({
        ...prev,
        current_password: '',
        new_password: '',
        confirm_password: ''
      }));
    } catch (err: any) {
      const errorMessage = err?.message || 'Failed to save account settings';
      alert(`❌ ${errorMessage}`);
      console.error('Error saving account settings:', err);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveOrderSettings = async () => {
    try {
      setSaving(true);
      
      // Save to backend API
      await apiClient.updateOrderSettings({
        delivery_available: orderSettings.delivery_available,
        auto_accept_orders: orderSettings.auto_accept_orders,
        default_preparation_time: orderSettings.default_preparation_time,
        minimum_order_value: orderSettings.minimum_order_value,
        maximum_order_value: orderSettings.maximum_order_value || undefined,
        allow_order_modifications: orderSettings.allow_order_modifications,
        cancellation_policy: orderSettings.cancellation_policy || undefined,
      });
      
      alert('✅ Order settings saved successfully to database!');
    } catch (err) {
      console.error('Failed to save order settings:', err);
      alert('Failed to save order settings: ' + (err instanceof Error ? err.message : 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  const handleGetLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setProfileSettings(prev => ({
            ...prev,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          }));
        },
        (error) => {
          alert('Failed to get location. Please enter manually.');
        }
      );
    } else {
      alert('Geolocation is not supported by your browser.');
    }
  };

  // Show loading spinner with timeout message
  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading settings...</p>
          <p className="mt-2 text-sm text-gray-500">If this takes too long, check if the backend server is running</p>
          <button
            onClick={() => {
              setLoading(false);
              alert('Loading cancelled. Page will load with limited functionality.');
            }}
            className="mt-4 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Cancel Loading
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => router.push('/dashboard')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <svg className="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>
              <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 lg:px-8 py-6">
        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6" aria-label="Tabs">
              {[
                { id: 'notifications', name: '🔔 Notifications', icon: '🔔' },
                { id: 'subscription', name: '💳 Subscription', icon: '💳' },
                { id: 'payments', name: '💵 Payments', icon: '💵' },
                { id: 'profile', name: '🏪 Profile', icon: '🏪' },
                { id: 'account', name: '👤 Account', icon: '👤' },
                { id: 'orders', name: '📦 Orders', icon: '📦' },
                { id: 'support', name: '📞 Support & Contact', icon: '📞' },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          {/* Notifications Tab */}
          {activeTab === 'notifications' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Notification Settings</h2>
                <p className="text-gray-600">Manage how and when you receive notifications</p>
              </div>

              {/* WhatsApp Notifications */}
              <div className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                      <span>📱</span> WhatsApp Notifications
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">Receive notifications on your WhatsApp number</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notificationSettings.whatsapp_enabled}
                      onChange={(e) => setNotificationSettings(prev => ({ ...prev, whatsapp_enabled: e.target.checked }))}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
                
                {notificationSettings.whatsapp_enabled && (
                  <div className="space-y-4 mt-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        WhatsApp Number
                      </label>
                      <input
                        type="text"
                        value={notificationSettings.whatsapp_number}
                        readOnly
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-600"
                        placeholder="WhatsApp number"
                      />
                      <p className="text-xs text-gray-500 mt-1">This is your registered WhatsApp Business number</p>
                    </div>
                    
                    <button
                      onClick={handleTestNotification}
                      disabled={saving}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {saving ? '⏳ Sending...' : '📱 Send Test Notification'}
                    </button>
                  </div>
                )}
              </div>

              {/* Email Notifications */}
              <div className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                      <span>📧</span> Email Notifications
                    </h3>
                    <p className="text-sm text-gray-600 mt-1">Receive email notifications for important updates</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={notificationSettings.email_enabled}
                      onChange={(e) => setNotificationSettings(prev => ({ ...prev, email_enabled: e.target.checked }))}
                      className="sr-only peer"
                    />
                    <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
                
                {notificationSettings.email_enabled && (
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={notificationSettings.email_address}
                      onChange={(e) => setNotificationSettings(prev => ({ ...prev, email_address: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="your@email.com"
                    />
                  </div>
                )}
              </div>

              {/* Order Status Notifications */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Status Notifications</h3>
                <p className="text-sm text-gray-600 mb-4">Select which order statuses you want to be notified about</p>
                
                <div className="space-y-3">
                  {[
                    { key: 'notify_new_order', label: 'New Order (Pending)', icon: '🆕' },
                    { key: 'notify_preparing', label: 'Order Preparing', icon: '👨‍🍳' },
                    { key: 'notify_ready', label: 'Order Ready', icon: '✅' },
                    { key: 'notify_delivered', label: 'Order Delivered', icon: '🚚' },
                    { key: 'notify_cancelled', label: 'Order Cancelled', icon: '❌' },
                    { key: 'notify_payment', label: 'Payment Received', icon: '💳' },
                  ].map((item) => (
                    <label key={item.key} className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                      <div className="flex items-center gap-3">
                        <span className="text-base">{item.icon}</span>
                        <span className="text-sm font-medium text-gray-700">{item.label}</span>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={notificationSettings[item.key as keyof NotificationSettings] as boolean}
                          onChange={(e) => setNotificationSettings(prev => ({ ...prev, [item.key]: e.target.checked }))}
                          className="sr-only peer"
                        />
                        <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                      </label>
                    </label>
                  ))}
                </div>
              </div>

              {/* Sound & Visual Alerts */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Sound & Visual Alerts</h3>
                
                <div className="space-y-4">
                  <label className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">🔊</span>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Sound Notifications</span>
                        <p className="text-xs text-gray-500">Play beep sound for new orders</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notificationSettings.sound_enabled}
                        onChange={(e) => setNotificationSettings(prev => ({ ...prev, sound_enabled: e.target.checked }))}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </label>

                  <label className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">✨</span>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Blinking Animation</span>
                        <p className="text-xs text-gray-500">Blink sections when new orders arrive</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={notificationSettings.blink_enabled}
                        onChange={(e) => setNotificationSettings(prev => ({ ...prev, blink_enabled: e.target.checked }))}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveNotifications}
                  disabled={saving}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          )}

          {/* Subscription Tab */}
          {activeTab === 'subscription' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Subscription Management</h2>
                <p className="text-gray-600">Manage your subscription plan and billing</p>
              </div>

              {/* Current Plan */}
              <div className="border-2 border-blue-200 rounded-lg p-6 bg-gradient-to-br from-blue-50 to-white">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">{subscriptionInfo.plan_name}</h3>
                    <p className="text-gray-600 mt-1">
                      {subscriptionInfo.plan_type === 'free' && 'Perfect for getting started'}
                      {subscriptionInfo.plan_type === 'basic' && 'Essential features for small restaurants'}
                      {subscriptionInfo.plan_type === 'pro' && 'Advanced features for growing businesses'}
                      {subscriptionInfo.plan_type === 'enterprise' && 'Full features for large operations'}
                    </p>
                  </div>
                  <span className={`px-4 py-2 rounded-full text-sm font-semibold ${
                    subscriptionInfo.status === 'active' ? 'bg-green-100 text-green-800' :
                    subscriptionInfo.status === 'expired' ? 'bg-red-100 text-red-800' :
                    subscriptionInfo.status === 'trial' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {subscriptionInfo.status.toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-2 gap-4 mt-6">
                  <div>
                    <p className="text-sm text-gray-600">Billing Cycle</p>
                    <p className="text-lg font-semibold text-gray-900 capitalize">{subscriptionInfo.billing_cycle}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Next Billing Date</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {new Date(subscriptionInfo.expiry_date).toLocaleDateString()}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Auto-Renewal</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {subscriptionInfo.auto_renewal ? 'Enabled' : 'Disabled'}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">Started On</p>
                    <p className="text-lg font-semibold text-gray-900">
                      {new Date(subscriptionInfo.start_date).toLocaleDateString()}
                    </p>
                  </div>
                </div>
              </div>

              {/* Plan Features */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Plan Features</h3>
                <div className="space-y-2">
                  {subscriptionInfo.plan_type === 'free' && (
                    <>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> Up to 50 orders/month
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> Basic menu management
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> WhatsApp notifications
                      </div>
                    </>
                  )}
                  {subscriptionInfo.plan_type === 'basic' && (
                    <>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> Up to 500 orders/month
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> Full menu management
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> All notifications
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> Basic analytics
                      </div>
                    </>
                  )}
                  {subscriptionInfo.plan_type === 'pro' && (
                    <>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> Unlimited orders
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> Advanced analytics
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> Priority support
                      </div>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <span className="text-green-500">✓</span> API access
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Plan Comparison Table */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Available Plans</h3>
                
                {/* Billing Cycle Toggle */}
                <div className="flex items-center justify-center gap-4 mb-6">
                  <button
                    onClick={() => setBillingCycle('monthly')}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      billingCycle === 'monthly'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    Monthly
                  </button>
                  <button
                    onClick={() => setBillingCycle('annual')}
                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                      billingCycle === 'annual'
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    }`}
                  >
                    Annual
                    <span className="ml-2 text-xs bg-green-500 text-white px-2 py-0.5 rounded">Save 17%</span>
                  </button>
                </div>

                {/* Plans Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {plans.map((plan) => {
                    const isCurrentPlan = plan.type === subscriptionInfo.plan_type;
                    const price = billingCycle === 'monthly' ? plan.price_monthly : plan.price_annual;
                    const isUpgrade = ['basic', 'pro', 'enterprise'].includes(plan.type) && 
                                     ['free', 'basic', 'pro'].includes(subscriptionInfo.plan_type) &&
                                     plan.type !== subscriptionInfo.plan_type;
                    
                    return (
                      <div
                        key={plan.id}
                        className={`border-2 rounded-lg p-6 relative ${
                          isCurrentPlan
                            ? 'border-blue-500 bg-blue-50'
                            : 'border-gray-200 bg-white hover:border-blue-300 transition-colors'
                        }`}
                      >
                        {isCurrentPlan && (
                          <span className="absolute top-4 right-4 bg-blue-600 text-white px-2 py-1 rounded text-xs font-semibold">
                            Current Plan
                          </span>
                        )}
                        
                        <h4 className="text-xl font-bold text-gray-900 mb-2">{plan.name}</h4>
                        
                        <div className="mb-4">
                          <span className="text-3xl font-bold text-gray-900">₹{price.toLocaleString()}</span>
                          <span className="text-gray-600">
                            {price > 0 ? `/${billingCycle === 'monthly' ? 'mo' : 'yr'}` : '/forever'}
                          </span>
                        </div>

                        <div className="space-y-2 mb-6">
                          {plan.features.map((feature, idx) => (
                            <div key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                              <span className="text-green-500 mt-0.5">✓</span>
                              <span>{feature}</span>
                            </div>
                          ))}
                        </div>

                        <button
                          onClick={() => {
                            if (isUpgrade || !isCurrentPlan) {
                              handleUpgradePlan(plan);
                            }
                          }}
                          disabled={isCurrentPlan}
                          className={`w-full py-2 px-4 rounded-lg font-semibold transition-colors ${
                            isCurrentPlan
                              ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                              : 'bg-blue-600 text-white hover:bg-blue-700'
                          }`}
                        >
                          {isCurrentPlan ? 'Current Plan' : isUpgrade ? 'Upgrade Now' : 'Select Plan'}
                        </button>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Actions */}
              <div className="flex flex-wrap gap-3">
                <button
                  onClick={() => setShowPaymentHistory(true)}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors flex items-center gap-2"
                >
                  <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  View Payment History
                </button>
                {subscriptionInfo.auto_renewal && (
                  <button
                    onClick={() => {
                      if (confirm('Are you sure you want to cancel auto-renewal? Your subscription will remain active until the end of the billing period.')) {
                        setSubscriptionInfo(prev => ({ ...prev, auto_renewal: false }));
                        alert('Auto-renewal cancelled successfully.');
                      }
                    }}
                    className="px-6 py-2 border border-red-300 rounded-lg text-red-700 hover:bg-red-50 transition-colors"
                  >
                    Cancel Auto-Renewal
                  </button>
                )}
              </div>
            </div>
          )}

          {/* Payments Tab */}
          {activeTab === 'payments' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Payment Settings</h2>
                <p className="text-gray-600">Manage your UPI payment methods and QR codes</p>
              </div>

              {/* UPI ID Management */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">💳 UPI ID Configuration</h3>
                <p className="text-sm text-gray-600 mb-4">
                  Set up your UPI ID for receiving payments from customers. This will be used for payment links and QR code generation.
                </p>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      UPI ID *
                    </label>
                    <input
                      type="text"
                      value={restaurantInfo?.upi_id || ''}
                      onChange={(e) => {
                        const value = e.target.value;
                        setRestaurantInfo(prev => prev ? { ...prev, upi_id: value } : prev);
                      }}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg font-mono text-sm"
                      placeholder="restaurant@paytm / 1234567890@upi"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      {restaurantInfo?.upi_id 
                        ? `Current UPI ID: ${restaurantInfo.upi_id}` 
                        : 'Enter your UPI ID above (e.g., restaurant@paytm or 1234567890@upi).'}
                    </p>
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="button"
                      onClick={async () => {
                        try {
                          const upiId = restaurantInfo?.upi_id?.trim() || '';
                          if (!upiId) {
                            alert('Please enter a valid UPI ID before saving.');
                            return;
                          }

                          // Basic front-end validation
                          if (!upiId.includes('@')) {
                            alert('Invalid UPI ID. It should look like restaurant@paytm or 1234567890@upi');
                            return;
                          }

                          const updated = await apiClient.updateUPIID(upiId);
                          setRestaurantInfo(updated);
                          alert(`✅ UPI ID saved successfully: ${updated.upi_id}`);
                        } catch (err) {
                          console.error('Failed to update UPI ID:', err);
                          const message = err instanceof Error ? err.message : 'Unknown error';
                          alert(`❌ Failed to update UPI ID: ${message}`);
                        }
                      }}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                    >
                      Save UPI ID
                    </button>
                  </div>
                </div>
              </div>

              {/* UPI QR Code Management */}
              <div className="border border-gray-200 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900">📱 UPI QR Code</h3>
                  <button
                    onClick={async () => {
                      try {
                        // Add timeout
                        const timeoutPromise = new Promise((_, reject) => 
                          setTimeout(() => reject(new Error('Request timeout - backend may not be responding')), 8000)
                        );
                        
                        const infoPromise = apiClient.getRestaurantInfo();
                        const info = await Promise.race([infoPromise, timeoutPromise]) as any;
                        
                        setRestaurantInfo(info);
                        if (info.upi_qr_code && info.upi_qr_code.trim().length > 0) {
                          setUpiQrCode(info.upi_qr_code);
                          alert('✅ QR code refreshed from database!');
                        } else {
                          setUpiQrCode('');
                          alert('ℹ️ No QR code found in database');
                        }
                      } catch (err) {
                        const errorMessage = err instanceof Error ? err.message : 'Unknown error';
                        console.error('Failed to refresh QR code:', err);
                        
                        // Check if it's a network error
                        if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Network error') || errorMessage.includes('timeout')) {
                          alert('⚠️ Cannot connect to backend server.\n\nPlease ensure:\n1. Backend is running on port 4000\n2. Backend is accessible\n3. No firewall blocking the connection\n\nCurrent QR code will remain displayed if available.');
                        } else {
                          alert('⚠️ Failed to refresh QR code: ' + errorMessage);
                        }
                      }
                    }}
                    className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    title="Refresh QR code from database"
                  >
                    🔄 Refresh
                  </button>
                </div>
                <p className="text-sm text-gray-600 mb-4">
                  Upload your UPI QR code image or generate one from your UPI ID. This QR code will be displayed when customers click the UPI button on the dashboard.
                </p>
                
                <div className="space-y-4">
                  {/* Current QR Code Display */}
                  {upiQrCode ? (
                    <div className="flex flex-col items-center p-6 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg border-2 border-dashed border-blue-300">
                      <div className="bg-white p-4 rounded-lg shadow-lg cursor-pointer hover:shadow-xl transition-shadow" onClick={() => setShowQrCodeModal(true)}>
                        <img 
                          src={upiQrCode} 
                          alt="UPI QR Code" 
                          className="w-[500px] h-[500px] object-contain mb-3"
                          onError={(e) => {
                            console.error('Error loading QR code image');
                            const target = e.currentTarget;
                            target.style.display = 'none';
                            // Show error message
                            const parent = target.parentElement;
                            if (parent) {
                              parent.innerHTML = '<p class="text-red-600 text-sm">Error loading QR code image. Please try uploading again.</p>';
                            }
                          }}
                          onLoad={() => {
                            console.log('QR code image loaded successfully');
                          }}
                        />
                      </div>
                      <p className="text-sm font-semibold text-gray-700 mt-2">Current QR Code</p>
                      <p className="text-xs text-gray-500 mt-1">Click to view larger</p>
                      {restaurantInfo?.upi_id && (
                        <p className="text-xs text-gray-500 mt-1">UPI ID: {restaurantInfo.upi_id}</p>
                      )}
                    </div>
                  ) : (
                    <div className="flex flex-col items-center p-8 bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                      <svg className="w-24 h-24 text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                      </svg>
                      <p className="text-gray-600 font-medium">No QR Code Set</p>
                      <p className="text-xs text-gray-500 mt-1">Upload or generate a QR code below</p>
                    </div>
                  )}

                  {/* Upload QR Code */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      📤 Upload QR Code Image
                    </label>
                    <div className="flex items-center gap-3">
                      <input
                        type="file"
                        accept="image/*"
                        onChange={handleQrCodeFileChange}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <p className="text-xs text-gray-500 mt-1">Supported formats: PNG, JPG, JPEG (Max 5MB)</p>
                  </div>

                  {/* Generate QR Code */}
                  {restaurantInfo?.upi_id ? (
                    <div>
                      <button
                        type="button"
                        onClick={handleGenerateQrCode}
                        className="w-full px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center justify-center gap-2"
                      >
                        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
                        </svg>
                        Generate QR Code from UPI ID
                      </button>
                      <p className="text-xs text-gray-500 mt-1 text-center">Current UPI ID: <span className="font-mono font-semibold">{restaurantInfo.upi_id}</span></p>
                    </div>
                  ) : (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <p className="text-sm text-yellow-900">
                        ⚠️ <strong>UPI ID Required:</strong> Please set up your UPI ID first using the "UPI" button on the Dashboard before generating a QR code.
                      </p>
                    </div>
                  )}

                  {/* Save Button */}
                  <div className="pt-4 border-t">
                    <button
                      type="button"
                      onClick={handleSaveQrCode}
                      disabled={savingQrCode || !upiQrCode}
                      className="w-full px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-semibold disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    >
                      {savingQrCode ? (
                        <>
                          <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                          </svg>
                          Saving...
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                          </svg>
                          Save QR Code
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>

              {/* Payment Verification Info */}
              <div className="border border-gray-200 rounded-lg p-6 bg-gradient-to-br from-green-50 to-blue-50">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">✅ Payment Verification</h3>
                <div className="space-y-3">
                  <div className="flex items-start gap-3">
                    <span className="text-xl">💡</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900">How it works:</p>
                      <p className="text-xs text-gray-600 mt-1">
                        When customers make UPI payments, you can verify them on the Dashboard by entering the customer's UPI name from the payment notification.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-xl">📱</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900">QR Code Display:</p>
                      <p className="text-xs text-gray-600 mt-1">
                        The saved QR code will be displayed when customers click the "UPI" button on your Dashboard. They can scan it to make payments directly.
                      </p>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <span className="text-xl">🔒</span>
                    <div>
                      <p className="text-sm font-medium text-gray-900">Security:</p>
                      <p className="text-xs text-gray-600 mt-1">
                        Your UPI ID and QR code are securely stored and only accessible to authenticated restaurant owners.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Restaurant Profile</h2>
                <p className="text-gray-600">Manage your restaurant information and business details</p>
              </div>

              {/* Basic Information */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Basic Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Restaurant Name *
                    </label>
                    <input
                      type="text"
                      value={profileSettings.restaurant_name}
                      onChange={(e) => setProfileSettings(prev => ({ ...prev, restaurant_name: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Enter restaurant name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number *
                    </label>
                    <input
                      type="tel"
                      value={profileSettings.phone}
                      onChange={(e) => setProfileSettings(prev => ({ ...prev, phone: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="+91 9876543210"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={profileSettings.email}
                      onChange={(e) => setProfileSettings(prev => ({ ...prev, email: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="restaurant@example.com"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Address *
                    </label>
                    <textarea
                      value={profileSettings.address}
                      onChange={(e) => setProfileSettings(prev => ({ ...prev, address: e.target.value }))}
                      rows={3}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Enter full address"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Latitude
                    </label>
                    <div className="flex gap-2">
                      <input
                        type="number"
                        step="any"
                        value={profileSettings.latitude}
                        onChange={(e) => setProfileSettings(prev => ({ ...prev, latitude: parseFloat(e.target.value) || 0 }))}
                        className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        placeholder="26.7756833"
                      />
                      <button
                        type="button"
                        onClick={handleGetLocation}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm"
                      >
                        📍 Get Location
                      </button>
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Longitude
                    </label>
                    <input
                      type="number"
                      step="any"
                      value={profileSettings.longitude}
                      onChange={(e) => setProfileSettings(prev => ({ ...prev, longitude: parseFloat(e.target.value) || 0 }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="80.91468"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Delivery Radius (km)
                    </label>
                    <input
                      type="number"
                      value={profileSettings.delivery_radius}
                      onChange={(e) => setProfileSettings(prev => ({ ...prev, delivery_radius: parseInt(e.target.value) || 0 }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      min="1"
                      max="50"
                    />
                  </div>
                </div>
              </div>

              {/* Business Details */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Business Details</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      GST Number
                    </label>
                    <input
                      type="text"
                      value={profileSettings.gst_number}
                      onChange={(e) => setProfileSettings(prev => ({ ...prev, gst_number: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="29ABCDE1234F1Z5"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      PAN Number
                    </label>
                    <input
                      type="text"
                      value={profileSettings.pan_number}
                      onChange={(e) => setProfileSettings(prev => ({ ...prev, pan_number: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="ABCDE1234F"
                    />
                  </div>
                  <div className="md:col-span-2">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      FSSAI License Number
                    </label>
                    <input
                      type="text"
                      value={profileSettings.fssai_number}
                      onChange={(e) => setProfileSettings(prev => ({ ...prev, fssai_number: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="12345678901234"
                    />
                  </div>
                </div>
              </div>

              {/* Operating Hours */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Operating Hours</h3>
                <div className="space-y-3">
                  {Object.entries(profileSettings.operating_hours).map(([day, hours]) => (
                    <div key={day} className="flex items-center gap-4">
                      <div className="w-24">
                        <span className="text-sm font-medium text-gray-700 capitalize">{day}</span>
                      </div>
                      <label className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={!hours.closed}
                          onChange={(e) => setProfileSettings(prev => ({
                            ...prev,
                            operating_hours: {
                              ...prev.operating_hours,
                              [day]: { ...hours, closed: !e.target.checked }
                            }
                          }))}
                          className="h-4 w-4 text-blue-600"
                        />
                        <span className="text-sm text-gray-600">Open</span>
                      </label>
                      {!hours.closed && (
                        <>
                          <input
                            type="time"
                            value={hours.open}
                            onChange={(e) => setProfileSettings(prev => ({
                              ...prev,
                              operating_hours: {
                                ...prev.operating_hours,
                                [day]: { ...hours, open: e.target.value }
                              }
                            }))}
                            className="px-3 py-1 border border-gray-300 rounded-lg"
                          />
                          <span className="text-gray-500">to</span>
                          <input
                            type="time"
                            value={hours.close}
                            onChange={(e) => setProfileSettings(prev => ({
                              ...prev,
                              operating_hours: {
                                ...prev.operating_hours,
                                [day]: { ...hours, close: e.target.value }
                              }
                            }))}
                            className="px-3 py-1 border border-gray-300 rounded-lg"
                          />
                        </>
                      )}
                      {hours.closed && (
                        <span className="text-sm text-red-600">Closed</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveProfile}
                  disabled={saving}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          )}

          {/* Account Tab */}
          {activeTab === 'account' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Account Settings</h2>
                <p className="text-gray-600">Manage your account security and preferences</p>
              </div>

              {/* Owner Information */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Owner Information</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Owner Name *
                    </label>
                    <input
                      type="text"
                      value={accountSettings.owner_name}
                      onChange={(e) => setAccountSettings(prev => ({ ...prev, owner_name: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Enter owner name"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Owner Email *
                    </label>
                    <input
                      type="email"
                      value={accountSettings.owner_email}
                      onChange={(e) => setAccountSettings(prev => ({ ...prev, owner_email: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="owner@example.com"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Owner Phone *
                    </label>
                    <input
                      type="tel"
                      value={accountSettings.owner_phone}
                      onChange={(e) => setAccountSettings(prev => ({ ...prev, owner_phone: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="+91 9876543210"
                    />
                  </div>
                </div>
              </div>

              {/* Password Change */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Change Password</h3>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Current Password
                    </label>
                    <input
                      type="password"
                      value={accountSettings.current_password}
                      onChange={(e) => setAccountSettings(prev => ({ ...prev, current_password: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Enter current password"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      New Password
                    </label>
                    <input
                      type="password"
                      value={accountSettings.new_password}
                      onChange={(e) => setAccountSettings(prev => ({ ...prev, new_password: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Enter new password (min 6 characters)"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Confirm New Password
                    </label>
                    <input
                      type="password"
                      value={accountSettings.confirm_password}
                      onChange={(e) => setAccountSettings(prev => ({ ...prev, confirm_password: e.target.value }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Confirm new password"
                    />
                  </div>
                </div>
              </div>

              {/* Security Settings */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Security Settings</h3>
                <div className="space-y-4">
                  <label className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">🔒</span>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Two-Factor Authentication</span>
                        <p className="text-xs text-gray-500">Add an extra layer of security to your account</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={accountSettings.two_factor_enabled}
                        onChange={(e) => setAccountSettings(prev => ({ ...prev, two_factor_enabled: e.target.checked }))}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </label>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveAccount}
                  disabled={saving}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          )}

          {/* Orders Tab */}
          {activeTab === 'orders' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Order Settings</h2>
                <p className="text-gray-600">Configure how orders are processed and managed</p>
              </div>

              {/* Order Processing */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Processing</h3>
                <div className="space-y-4">
                  <label className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">🚚</span>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Delivery Available</span>
                        <p className="text-xs text-gray-500">Allow customers to place delivery orders</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={orderSettings.delivery_available}
                        onChange={(e) => setOrderSettings(prev => ({ ...prev, delivery_available: e.target.checked }))}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </label>
                  <label className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">✅</span>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Auto-Accept Orders</span>
                        <p className="text-xs text-gray-500">Automatically accept all incoming orders</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={orderSettings.auto_accept_orders}
                        onChange={(e) => setOrderSettings(prev => ({ ...prev, auto_accept_orders: e.target.checked }))}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </label>
                  <label className="flex items-center justify-between p-3 hover:bg-gray-50 rounded-lg cursor-pointer">
                    <div className="flex items-center gap-3">
                      <span className="text-xl">✏️</span>
                      <div>
                        <span className="text-sm font-medium text-gray-700">Allow Order Modifications</span>
                        <p className="text-xs text-gray-500">Allow customers to modify orders after placing</p>
                      </div>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={orderSettings.allow_order_modifications}
                        onChange={(e) => setOrderSettings(prev => ({ ...prev, allow_order_modifications: e.target.checked }))}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </label>
                </div>
              </div>

              {/* Order Limits */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Order Limits</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Minimum Order Value (₹)
                    </label>
                    <input
                      type="number"
                      value={orderSettings.minimum_order_value}
                      onChange={(e) => setOrderSettings(prev => ({ ...prev, minimum_order_value: parseFloat(e.target.value) || 0 }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      min="0"
                      step="0.01"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Maximum Order Value (₹)
                    </label>
                    <input
                      type="number"
                      value={orderSettings.maximum_order_value || ''}
                      onChange={(e) => setOrderSettings(prev => ({ ...prev, maximum_order_value: e.target.value ? parseFloat(e.target.value) : null }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      min="0"
                      step="0.01"
                      placeholder="No limit"
                    />
                    <p className="text-xs text-gray-500 mt-1">Leave empty for no limit</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Default Preparation Time (minutes)
                    </label>
                    <input
                      type="number"
                      value={orderSettings.default_preparation_time}
                      onChange={(e) => setOrderSettings(prev => ({ ...prev, default_preparation_time: parseInt(e.target.value) || 0 }))}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      min="5"
                      max="180"
                    />
                  </div>
                </div>
              </div>

              {/* Cancellation Policy */}
              <div className="border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Cancellation Policy</h3>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Policy Description
                  </label>
                  <textarea
                    value={orderSettings.cancellation_policy}
                    onChange={(e) => setOrderSettings(prev => ({ ...prev, cancellation_policy: e.target.value }))}
                    rows={4}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Describe your order cancellation policy..."
                  />
                  <p className="text-xs text-gray-500 mt-1">This will be displayed to customers</p>
                </div>
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t">
                <button
                  onClick={() => router.push('/dashboard')}
                  className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSaveOrderSettings}
                  disabled={saving}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {saving ? 'Saving...' : 'Save Changes'}
                </button>
              </div>
            </div>
          )}

          {/* Support & Contact Tab */}
          {activeTab === 'support' && (
            <div className="space-y-6">
              <div>
                <h2 className="text-xl font-bold text-gray-900 mb-2">Support & Contact</h2>
                <p className="text-gray-600">Get help, contact our support team, or reach out for assistance</p>
              </div>

              {/* Company Information */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-6 border-2 border-blue-100">
                <div className="flex items-start gap-4 mb-6">
                  <div className="bg-gradient-to-br from-blue-600 to-indigo-600 rounded-xl p-4 flex-shrink-0">
                    <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-bold text-gray-900 mb-2">WhatsApp Ordering Platform</h3>
                    <p className="text-gray-700 mb-1">
                      Professional restaurant management system powered by WhatsApp Business API
                    </p>
                    <p className="text-sm text-gray-600">
                      Helping restaurants manage orders, customers, and deliveries efficiently through WhatsApp
                    </p>
                  </div>
                </div>
              </div>

              {/* Contact Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Primary Contact */}
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-blue-400 hover:shadow-lg transition-all">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="bg-green-100 rounded-full p-3">
                      <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">Primary Contact</h3>
                      <p className="text-sm text-gray-600">Available Mon-Sat, 9 AM - 8 PM</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <a
                      href="tel:+919452151637"
                      className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-green-50 transition-colors group"
                    >
                      <div className="bg-green-100 rounded-lg p-2 group-hover:bg-green-200 transition-colors">
                        <svg className="w-5 h-5 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-500 mb-1">Phone / WhatsApp</p>
                        <p className="text-lg font-bold text-gray-900">+91 94521 51637</p>
                      </div>
                      <svg className="w-5 h-5 text-gray-400 group-hover:text-green-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </a>
                    <a
                      href="https://wa.me/919452151637"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center gap-2 w-full bg-green-500 text-white py-3 px-4 rounded-lg font-semibold hover:bg-green-600 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                      </svg>
                      Chat on WhatsApp
                    </a>
                  </div>
                </div>

                {/* Secondary Contact */}
                <div className="bg-white border-2 border-gray-200 rounded-xl p-6 hover:border-blue-400 hover:shadow-lg transition-all">
                  <div className="flex items-center gap-4 mb-4">
                    <div className="bg-blue-100 rounded-full p-3">
                      <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                      </svg>
                    </div>
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">Alternative Contact</h3>
                      <p className="text-sm text-gray-600">Backup support line</p>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <a
                      href="tel:+919151338489"
                      className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-blue-50 transition-colors group"
                    >
                      <div className="bg-blue-100 rounded-lg p-2 group-hover:bg-blue-200 transition-colors">
                        <svg className="w-5 h-5 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                        </svg>
                      </div>
                      <div className="flex-1">
                        <p className="text-xs text-gray-500 mb-1">Phone / WhatsApp</p>
                        <p className="text-lg font-bold text-gray-900">+91 91513 38489</p>
                      </div>
                      <svg className="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    </a>
                    <a
                      href="https://wa.me/919151338489"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center justify-center gap-2 w-full bg-blue-500 text-white py-3 px-4 rounded-lg font-semibold hover:bg-blue-600 transition-colors"
                    >
                      <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
                      </svg>
                      Chat on WhatsApp
                    </a>
                  </div>
                </div>
              </div>

              {/* Support Information Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                <div className="bg-white border border-gray-200 rounded-xl p-5 text-center">
                  <div className="bg-purple-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h4 className="font-bold text-gray-900 mb-1">Business Hours</h4>
                  <p className="text-sm text-gray-600">Monday - Saturday</p>
                  <p className="text-sm text-gray-600 font-semibold">9:00 AM - 8:00 PM</p>
                </div>

                <div className="bg-white border border-gray-200 rounded-xl p-5 text-center">
                  <div className="bg-green-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                  </div>
                  <h4 className="font-bold text-gray-900 mb-1">Response Time</h4>
                  <p className="text-sm text-gray-600">Usually within</p>
                  <p className="text-sm text-gray-600 font-semibold">1-2 Hours</p>
                </div>

                <div className="bg-white border border-gray-200 rounded-xl p-5 text-center">
                  <div className="bg-blue-100 rounded-full w-12 h-12 flex items-center justify-center mx-auto mb-3">
                    <svg className="w-6 h-6 text-blue-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <h4 className="font-bold text-gray-900 mb-1">Support Types</h4>
                  <p className="text-sm text-gray-600">Technical & Billing</p>
                  <p className="text-sm text-gray-600 font-semibold">24/7 Available</p>
                </div>
              </div>

              {/* Additional Information */}
              <div className="bg-gray-50 rounded-xl p-6 border border-gray-200">
                <h3 className="text-lg font-bold text-gray-900 mb-3 flex items-center gap-2">
                  <svg className="w-5 h-5 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  Need Help?
                </h3>
                <p className="text-gray-700 mb-4">
                  Our support team is here to help you with any questions, technical issues, or concerns about your restaurant management system. 
                  Feel free to reach out via phone or WhatsApp, and we'll get back to you as soon as possible.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-gray-600">
                  <div className="flex items-start gap-2">
                    <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Account setup and onboarding assistance</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Technical troubleshooting and bug fixes</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Billing and subscription inquiries</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <svg className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    <span>Feature requests and platform updates</span>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Payment Modal */}
      {showUpgradeModal && selectedPlan && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4 overflow-y-auto">
          <div className="bg-white rounded-xl max-w-2xl w-full my-8 shadow-2xl max-h-[90vh] overflow-y-auto">
            {/* Header */}
            <div className="sticky top-0 bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-4 py-3 rounded-t-xl flex items-center justify-between z-10">
              <div>
                <h2 className="text-lg font-bold">Complete Payment</h2>
                <p className="text-blue-100 text-xs mt-0.5">Upgrade to {selectedPlan.name}</p>
              </div>
              <button
                onClick={() => {
                  setShowUpgradeModal(false);
                  setSelectedPlan(null);
                }}
                className="text-white hover:bg-white/20 rounded-full p-2 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-4">
              {/* Plan Summary */}
              <div className="bg-gradient-to-br from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h3 className="text-lg font-bold text-gray-900">{selectedPlan.name}</h3>
                    <p className="text-gray-600 text-xs mt-0.5">
                      {billingCycle === 'monthly' ? 'Monthly Billing' : 'Annual Billing'}
                      {billingCycle === 'annual' && (
                        <span className="ml-2 bg-green-500 text-white px-1.5 py-0.5 rounded text-xs font-semibold">
                          Save 17%
                        </span>
                      )}
                    </p>
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold text-gray-900">
                      ₹{(billingCycle === 'monthly' ? selectedPlan.price_monthly : selectedPlan.price_annual).toLocaleString()}
                    </div>
                    <div className="text-xs text-gray-600">
                      {billingCycle === 'monthly' ? 'per month' : 'per year'}
                    </div>
                  </div>
                </div>
                
                {/* Features Preview */}
                <div className="border-t border-blue-200 pt-3 mt-3">
                  <p className="text-xs font-semibold text-gray-700 mb-1.5">Plan Features:</p>
                  <div className="grid grid-cols-2 gap-1.5">
                    {selectedPlan.features.slice(0, 4).map((feature, idx) => (
                      <div key={idx} className="flex items-center gap-1.5 text-xs text-gray-600">
                        <span className="text-green-500">✓</span>
                        <span className="truncate">{feature}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Payment Method Tabs */}
              <div className="mb-4">
                <div className="flex gap-1 border-b border-gray-200 overflow-x-auto">
                  {[
                    { id: 'card', label: '💳 Card', icon: '💳' },
                    { id: 'upi', label: '📱 UPI', icon: '📱' },
                    { id: 'wallet', label: '👛 Wallet', icon: '👛' },
                    { id: 'netbanking', label: '🏦 Banking', icon: '🏦' },
                  ].map((method) => (
                    <button
                      key={method.id}
                      onClick={() => setPaymentMethod(method.id as any)}
                      className={`px-3 py-2 text-sm font-semibold transition-colors border-b-2 whitespace-nowrap ${
                        paymentMethod === method.id
                          ? 'border-blue-600 text-blue-600 bg-blue-50'
                          : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                      }`}
                    >
                      {method.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Payment Forms */}
              <div className="mb-4">
                {/* Card Payment */}
                {paymentMethod === 'card' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Card Number *
                      </label>
                      <input
                        type="text"
                        value={cardDetails.cardNumber}
                        onChange={(e) => {
                          const formatted = formatCardNumber(e.target.value);
                          setCardDetails({ ...cardDetails, cardNumber: formatted });
                        }}
                        placeholder="1234 5678 9012 3456"
                        maxLength={19}
                        className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Card Holder Name *
                      </label>
                      <input
                        type="text"
                        value={cardDetails.cardHolder}
                        onChange={(e) => setCardDetails({ ...cardDetails, cardHolder: e.target.value.toUpperCase() })}
                        placeholder="JOHN DOE"
                        className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          Expiry Date *
                        </label>
                        <input
                          type="text"
                          value={cardDetails.expiryDate}
                          onChange={(e) => {
                            const formatted = formatExpiryDate(e.target.value);
                            setCardDetails({ ...cardDetails, expiryDate: formatted });
                          }}
                          placeholder="MM/YY"
                          maxLength={5}
                          className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-semibold text-gray-700 mb-2">
                          CVV *
                        </label>
                        <input
                          type="text"
                          value={cardDetails.cvv}
                          onChange={(e) => {
                            const v = e.target.value.replace(/[^0-9]/gi, '');
                            if (v.length <= 4) {
                              setCardDetails({ ...cardDetails, cvv: v });
                            }
                          }}
                          placeholder="123"
                          maxLength={4}
                          className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-2 flex items-start gap-2">
                      <svg className="w-4 h-4 text-blue-600 mt-0.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                      </svg>
                      <p className="text-xs text-blue-800">
                        Secured with 256-bit SSL encryption. We do not store your card details.
                      </p>
                    </div>
                  </div>
                )}

                {/* UPI Payment */}
                {paymentMethod === 'upi' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        UPI ID *
                      </label>
                      <input
                        type="text"
                        value={upiId}
                        onChange={(e) => setUpiId(e.target.value)}
                        placeholder="yourname@paytm / yourname@ybl / yourname@upi"
                        className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      />
                    </div>
                    <div className="bg-gradient-to-r from-purple-50 to-pink-50 border-2 border-purple-200 rounded-lg p-3">
                      <p className="text-xs font-semibold text-gray-700 mb-2">Supported UPI Apps:</p>
                      <div className="flex flex-wrap gap-2">
                        {['PhonePe', 'GPay', 'Paytm', 'BHIM', 'Amazon Pay'].map((app) => (
                          <div key={app} className="flex items-center gap-1.5 bg-white px-2 py-1.5 rounded-lg border border-gray-200">
                            <span className="text-sm">{app === 'PhonePe' ? '📱' : app === 'GPay' ? '💰' : app === 'Paytm' ? '💳' : app === 'BHIM' ? '🏦' : '🛒'}</span>
                            <span className="text-xs font-medium text-gray-700">{app}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                )}

                {/* Wallet Payment */}
                {paymentMethod === 'wallet' && (
                  <div className="space-y-3">
                    <p className="text-xs font-semibold text-gray-700 mb-2">Select Wallet:</p>
                    <div className="grid grid-cols-3 gap-2">
                      {[
                        { id: 'paytm', name: 'Paytm', icon: '💳', color: 'bg-blue-600' },
                        { id: 'phonepe', name: 'PhonePe', icon: '📱', color: 'bg-purple-600' },
                        { id: 'gpay', name: 'GPay', icon: '💰', color: 'bg-green-600' },
                      ].map((wallet) => (
                        <button
                          key={wallet.id}
                          onClick={() => setSelectedWallet(wallet.id as any)}
                          className={`p-3 rounded-lg border-2 transition-all ${
                            selectedWallet === wallet.id
                              ? 'border-blue-500 bg-blue-50'
                              : 'border-gray-200 hover:border-gray-300'
                          }`}
                        >
                          <div className="flex flex-col items-center gap-1.5">
                            <span className="text-xl">{wallet.icon}</span>
                            <span className="text-xs font-semibold text-gray-900">{wallet.name}</span>
                          </div>
                        </button>
                      ))}
                    </div>
                    {selectedWallet && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-2">
                        <p className="text-xs text-blue-800">
                          Redirecting to {selectedWallet === 'paytm' ? 'Paytm' : selectedWallet === 'phonepe' ? 'PhonePe' : 'Google Pay'}...
                        </p>
                      </div>
                    )}
                  </div>
                )}

                {/* Net Banking */}
                {paymentMethod === 'netbanking' && (
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-semibold text-gray-700 mb-2">
                        Select Bank *
                      </label>
                      <select
                        value={selectedBank}
                        onChange={(e) => setSelectedBank(e.target.value)}
                        className="w-full px-3 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value="">-- Select Bank --</option>
                        {[
                          'State Bank of India (SBI)',
                          'HDFC Bank',
                          'ICICI Bank',
                          'Axis Bank',
                          'Kotak Mahindra Bank',
                          'Punjab National Bank (PNB)',
                          'Bank of Baroda',
                          'Union Bank of India',
                          'Canara Bank',
                          'Indian Bank',
                        ].map((bank) => (
                          <option key={bank} value={bank}>
                            {bank}
                          </option>
                        ))}
                      </select>
                    </div>
                    {selectedBank && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-2">
                        <p className="text-xs text-blue-800">
                          Redirecting to {selectedBank} net banking portal...
                        </p>
                      </div>
                    )}
                  </div>
                )}
              </div>

              {/* Payment Summary */}
              <div className="bg-gray-50 border-2 border-gray-200 rounded-lg p-4 mb-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-gray-700 font-semibold">Subtotal:</span>
                  <span className="text-sm text-gray-900 font-bold">
                    ₹{(billingCycle === 'monthly' ? selectedPlan.price_monthly : selectedPlan.price_annual).toLocaleString()}
                  </span>
                </div>
                <div className="flex items-center justify-between mb-3">
                  <span className="text-sm text-gray-700 font-semibold">GST (18%):</span>
                  <span className="text-sm text-gray-900 font-bold">
                    ₹{Math.round((billingCycle === 'monthly' ? selectedPlan.price_monthly : selectedPlan.price_annual) * 0.18).toLocaleString()}
                  </span>
                </div>
                <div className="border-t-2 border-gray-300 pt-3 flex items-center justify-between">
                  <span className="text-lg font-bold text-gray-900">Total Amount:</span>
                  <span className="text-xl font-bold text-blue-600">
                    ₹{Math.round((billingCycle === 'monthly' ? selectedPlan.price_monthly : selectedPlan.price_annual) * 1.18).toLocaleString()}
                  </span>
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setShowUpgradeModal(false);
                    setSelectedPlan(null);
                  }}
                  className="flex-1 px-4 py-2.5 border-2 border-gray-300 rounded-lg text-gray-700 text-sm font-semibold hover:bg-gray-50 transition-colors"
                  disabled={processingPayment}
                >
                  Cancel
                </button>
                <button
                  onClick={handlePayment}
                  disabled={processingPayment}
                  className="flex-1 px-4 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-bold hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 text-sm"
                >
                  {processingPayment ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <span>Pay ₹{Math.round((billingCycle === 'monthly' ? selectedPlan.price_monthly : selectedPlan.price_annual) * 1.18).toLocaleString()}</span>
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Payment History Modal */}
      {showPaymentHistory && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="sticky top-0 bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-gray-900">Payment History</h2>
              <button
                onClick={() => setShowPaymentHistory(false)}
                className="text-gray-400 hover:text-gray-600 text-2xl"
              >
                ×
              </button>
            </div>
            <div className="p-6">
              {paymentHistory.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-600">No payment history available</p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Date</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Amount</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Transaction ID</th>
                        <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {paymentHistory.map((payment) => (
                        <tr key={payment.id} className="hover:bg-gray-50">
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                            {new Date(payment.date).toLocaleDateString()}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                            {payment.plan_name}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm font-semibold text-gray-900">
                            ₹{payment.amount.toLocaleString()}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap">
                            <span className={`px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              payment.status === 'success' ? 'bg-green-100 text-green-800' :
                              payment.status === 'failed' ? 'bg-red-100 text-red-800' :
                              'bg-yellow-100 text-yellow-800'
                            }`}>
                              {payment.status.toUpperCase()}
                            </span>
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                            {payment.transaction_id}
                          </td>
                          <td className="px-4 py-4 whitespace-nowrap text-sm">
                            {payment.invoice_url && (
                              <a
                                href={payment.invoice_url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-600 hover:text-blue-900"
                              >
                                Download Invoice
                              </a>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* QR Code Modal */}
      {showQrCodeModal && upiQrCode && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" onClick={() => setShowQrCodeModal(false)}>
          <div className="bg-white rounded-lg p-6 w-[600px] max-w-full relative" onClick={(e) => e.stopPropagation()}>
            <button
              onClick={() => setShowQrCodeModal(false)}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-3xl font-bold z-10 w-8 h-8 flex items-center justify-center"
            >
              ×
            </button>
            <h3 className="text-xl font-bold text-gray-900 mb-4 text-center">UPI QR Code</h3>
            <div className="flex flex-col items-center">
              <div className="bg-white p-4 rounded-lg shadow-xl">
                <img 
                  src={upiQrCode} 
                  alt="UPI QR Code" 
                  className="w-[550px] h-[550px] object-contain"
                  style={{ minWidth: '550px', minHeight: '550px' }}
                  onError={(e) => {
                    console.error('Error loading QR code image');
                    const target = e.currentTarget;
                    target.style.display = 'none';
                  }}
                />
              </div>
              {restaurantInfo?.upi_id && (
                <p className="text-sm text-gray-600 mt-4">UPI ID: <span className="font-semibold">{restaurantInfo.upi_id}</span></p>
              )}
              <p className="text-xs text-gray-500 mt-2">Scan this QR code to make payment</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

