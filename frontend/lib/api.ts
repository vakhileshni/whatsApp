// API Client for WhatsApp Ordering SaaS Backend

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:4000';

// Types
export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  restaurant_id: string;
  restaurant_name: string;
  restaurant_phone: string;
  user_name: string;
}

export interface Product {
  id: string;
  restaurant_id: string;
  name: string;
  description: string;
  price: number;
  discounted_price?: number;
  discount_percentage?: number;
  category: string;
  is_available: boolean;
}

export interface ProductCreate {
  name: string;
  description: string;
  price: number;
  discounted_price?: number;
  category: string;
  is_available?: boolean;
}

export interface ProductUpdate {
  name?: string;
  description?: string;
  price?: number;
  discounted_price?: number;
  category?: string;
  is_available?: boolean;
}

export interface OrderItem {
  product_id: string;
  product_name: string;
  quantity: number;
  price: number;
}

export interface Order {
  id: string;
  restaurant_id: string;
  customer_phone: string;
  customer_name: string;
  items: OrderItem[];
  order_type: string;
  subtotal: number;
  delivery_fee: number;
  total: number;
  status: string;
  created_at: string;
  updated_at: string;
  delivery_address?: string;
  payment_method?: string;  // "cod" or "online"
  payment_status?: string;  // "pending", "verified", "failed"
  payment_link?: string;  // UPI payment link or Razorpay payment link
  razorpay_payment_link_id?: string;  // Razorpay payment link ID for status polling
  customer_rating?: number;  // Rating given by customer (1-5)
  total_amount?: number;  // Alias for total
  customer_upi_name?: string;  // UPI name/number provided by customer
}

export interface DashboardStats {
  total_orders: number;
  pending_orders: number;
  preparing_orders: number;
  ready_orders: number;
  delivered_orders: number;
  total_revenue: number;
  today_orders: number;
}

export interface RestaurantInfo {
  id: string;
  name: string;
  phone: string;
  address?: string;
  latitude?: number;
  longitude?: number;
  delivery_fee?: number;
  cuisine_type?: string;
  upi_id: string;
  upi_qr_code?: string;  // UPI QR code image URL or base64
  twilio_number: string;  // WhatsApp Business number for QR codes
  is_active: boolean;  // Restaurant open/closed status
}

export interface NotificationSettings {
  whatsapp_notifications_enabled: boolean;
  whatsapp_number?: string;
  email_notifications_enabled: boolean;
  email_address?: string;
  sms_notifications_enabled: boolean;
  sms_number?: string;
  notify_new_order: boolean;
  notify_preparing: boolean;
  notify_ready: boolean;
  notify_delivered: boolean;
  notify_cancelled: boolean;
  notify_payment: boolean;
  sound_enabled: boolean;
  blink_enabled: boolean;
}

export interface OrderSettings {
  auto_accept_orders: boolean;
  default_preparation_time: number;
  minimum_order_value: number;
  maximum_order_value?: number;
  allow_order_modifications: boolean;
  cancellation_policy?: string;
  delivery_available: boolean;
}

export interface SettingsResponse extends NotificationSettings, OrderSettings {
  id: string;
  restaurant_id: string;
  // Profile / business settings from settings table
  delivery_radius_km?: number | null;
  gst_number?: string | null;
  pan_number?: string | null;
  fssai_number?: string | null;
  operating_hours?: string | null;
}

export interface CurrentUserProfile {
  user_id: string;
  restaurant_id: string;
  owner_name: string;
  owner_email: string;
  restaurant_name: string;
  restaurant_phone: string;
}

export interface Notification {
  id: string;
  restaurant_id: string;
  order_id: string | null;
  notification_type: string;
  notification_event: string;
  recipient: string;
  message_body: string;
  status: string;
  button_clicked: string | null;
  clicked_at: string | null;
  error_message: string | null;
  created_at: string | null;
  updated_at: string | null;
}

export interface NotificationStats {
  total: number;
  sent: number;
  delivered: number;
  failed: number;
  disabled: number;
  skipped: number;
  clicked: number;
  by_event: Record<string, number>;
}

export interface UpdateUPIRequest {
  upi_id: string;
  password: string;
}

export interface VerifyPaymentRequest {
  customer_upi_name: string;
}

export interface VerifyUPIRequest {
  upi_id: string;
  password: string;
}

export interface VerifyUPIResponse {
  status: string;
  message: string;
  upi_id: string;
  qr_data: string;
  verification_code: string;
  verification_amount: number;
  instructions: string;
}

// Token storage helpers
const getToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('auth_token');
  }
  return null;
};

const setToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('auth_token', token);
  }
};

const removeToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('auth_token');
  }
};

// API Client class
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {},
    requireAuth: boolean = true
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string> || {}),
    };

    // Add auth token if required
    if (requireAuth) {
      const token = getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    let response: Response;
    try {
      // Log request details for debugging
      console.log(`Making request to: ${url}`, {
        method: options.method || 'GET',
        headers: Object.keys(headers),
        baseUrl: this.baseUrl,
        hasToken: !!headers['Authorization']
      });

      // Create abort controller for timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000); // 10 second timeout
      
      try {
        response = await fetch(url, {
          ...options,
          headers,
          mode: 'cors', // Explicitly set CORS mode
          signal: controller.signal,
        });
        clearTimeout(timeoutId);
      } catch (fetchError: any) {
        clearTimeout(timeoutId);
        if (fetchError.name === 'AbortError') {
          throw new Error('Request timeout - backend server may not be responding');
        }
        throw fetchError;
      }
    } catch (error) {
      // Network error - backend server might not be running
      const errorMessage = error instanceof Error ? error.message : 'Network error';
      
      // Log detailed error for debugging (but don't spam console)
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        // Network/CORS error - only log in development, silently handle in production
        if (process.env.NODE_ENV === 'development') {
          console.warn(`⚠️ Network error: Cannot connect to backend at ${this.baseUrl}${endpoint}`, {
            possibleCauses: [
              'Backend server not responding',
              'CORS configuration issue',
              'Authentication token missing/invalid',
              'Firewall blocking connection'
            ],
            hasToken: !!headers['Authorization'],
            suggestion: 'Check backend logs and CORS configuration'
          });
        }
        // Don't log full error details - just create user-friendly error
      } else {
        // Other errors - log normally in development
        if (process.env.NODE_ENV === 'development') {
          console.error(`Failed to fetch ${url}:`, {
            error: errorMessage,
            url,
            baseUrl: this.baseUrl,
            errorType: error instanceof TypeError ? 'TypeError (CORS/Network)' : 'Other',
            errorName: error instanceof Error ? error.name : 'Unknown',
            hasToken: !!headers['Authorization']
          });
        }
      }
      
      // Create user-friendly error message
      if (error instanceof TypeError && error.message.includes('Failed to fetch')) {
        const networkError = new Error(
          `Cannot connect to backend server at ${this.baseUrl}`
        );
        (networkError as any).isNetworkError = true;
        (networkError as any).originalError = error;
        throw networkError;
      }
      
      // For other errors, throw as-is
      throw error;
    }

    if (!response.ok) {
      if (response.status === 401) {
        // Unauthorized - remove token and redirect to login
        removeToken();
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        throw new Error('Unauthorized');
      }

      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return response.json();
  }

  // Auth API
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await this.request<LoginResponse>(
      '/api/v1/auth/login',
      {
        method: 'POST',
        body: JSON.stringify(credentials),
      },
      false
    );
    
    // Store token
    setToken(response.access_token);
    
    // Store restaurant info
    if (typeof window !== 'undefined') {
      localStorage.setItem('restaurant_name', response.restaurant_name);
      localStorage.setItem('restaurant_id', response.restaurant_id);
      localStorage.setItem('restaurant_phone', response.restaurant_phone);
      localStorage.setItem('user_name', response.user_name);
    }
    
    return response;
  }

    logout(): void {
    removeToken();
    if (typeof window !== 'undefined') {
      localStorage.removeItem('restaurant_name');
      localStorage.removeItem('restaurant_id');
      localStorage.removeItem('restaurant_phone');
      localStorage.removeItem('user_name');
    }
  }

  getRestaurantInfoFromStorage(): {name: string; id: string; phone: string; user_name: string} | null {
    if (typeof window !== 'undefined') {
      const name = localStorage.getItem('restaurant_name');
      const id = localStorage.getItem('restaurant_id');
      const phone = localStorage.getItem('restaurant_phone') || '';
      const user_name = localStorage.getItem('user_name');
      if (name && id && user_name) {
        return { name, id, phone, user_name };
      }
    }
    return null;
  }

  isAuthenticated(): boolean {
    return getToken() !== null;
  }

  // Menu API
  async getMenu(): Promise<Product[]> {
    return this.request<Product[]>('/api/v1/menu');
  }

  async createProduct(product: ProductCreate): Promise<Product> {
    return this.request<Product>('/api/v1/menu', {
      method: 'POST',
      body: JSON.stringify(product),
    });
  }

  async updateProduct(productId: string, product: ProductUpdate): Promise<Product> {
    return this.request<Product>(`/api/v1/menu/${productId}`, {
      method: 'PUT',
      body: JSON.stringify(product),
    });
  }

  async deleteProduct(productId: string): Promise<void> {
    return this.request<void>(`/api/v1/menu/${productId}`, {
      method: 'DELETE',
    });
  }

  // Orders API
  async getOrders(): Promise<Order[]> {
    return this.request<Order[]>('/api/v1/orders');
  }

  async getOrder(orderId: string): Promise<Order> {
    return this.request<Order>(`/api/v1/orders/${orderId}`);
  }

  async updateOrderStatus(orderId: string, status: string): Promise<Order> {
    return this.request<Order>(`/api/v1/orders/${orderId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  // Dashboard API
  async getDashboardStats(): Promise<DashboardStats> {
    return this.request<DashboardStats>('/api/v1/dashboard/stats');
  }

  async getRestaurantInfo(): Promise<RestaurantInfo> {
    return this.request<RestaurantInfo>('/api/v1/dashboard/restaurant');
  }

  async updateUPIID(upi_id: string): Promise<RestaurantInfo> {
    return this.request<RestaurantInfo>('/api/v1/dashboard/restaurant/upi-id', {
      method: 'PUT',
      body: JSON.stringify({ upi_id }),
    });
  }

  async confirmUPIVerification(verification_code: string, upi_id: string, password?: string, new_password?: string): Promise<RestaurantInfo> {
    return this.request<RestaurantInfo>('/api/v1/dashboard/restaurant/upi/confirm-verification', {
      method: 'POST',
      body: JSON.stringify({ 
        verification_code,
        upi_id, 
        password: password || undefined,
        new_password: new_password || undefined
      }),
    });
  }

  async updateRestaurantStatus(is_active: boolean): Promise<RestaurantInfo> {
    return this.request<RestaurantInfo>('/api/v1/dashboard/restaurant/status', {
      method: 'PATCH',
      body: JSON.stringify({ is_active }),
    });
  }

  async verifyPayment(orderId: string, customer_upi_name: string, amount_paid?: number): Promise<Order> {
    // If amount_paid not provided, it will be set to order total in backend
    const payload: any = { customer_upi_name };
    if (amount_paid !== undefined) {
      payload.amount_paid = amount_paid;
    }
    return this.request<Order>(`/api/v1/orders/${orderId}/verify-payment`, {
      method: 'PATCH',
      body: JSON.stringify(payload),
    });
  }

  async verifyPaymentPublic(orderId: string, customer_upi_name: string, amount_paid: number): Promise<{ success: boolean; message: string; order: Order }> {
    // Public endpoint - no auth required
    const response = await fetch(`${API_BASE_URL}/api/v1/orders/${orderId}/verify-payment-public`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ customer_upi_name, amount_paid }),
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
      throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }
    
    return response.json();
  }

  async verifyRestaurantUPI(upi_id: string, password?: string): Promise<VerifyUPIResponse> {
    return this.request<VerifyUPIResponse>('/api/v1/dashboard/restaurant/upi/verify', {
      method: 'POST',
      body: JSON.stringify({ upi_id, password: password || undefined }),
    });
  }

  async saveUPIQRCode(upi_qr_code: string): Promise<RestaurantInfo> {
    return this.request<RestaurantInfo>('/api/v1/dashboard/restaurant/upi/qr-code', {
      method: 'POST',
      body: JSON.stringify({ upi_qr_code }),
    });
  }

  async getQRCodeHistory(limit: number = 10): Promise<{
    restaurant_id: string;
    total_versions: number;
    history: Array<{
      id: string;
      restaurant_id: string;
      upi_qr_code: string;
      version_number: number;
      is_current: boolean;
      effective_from: string;
      effective_to: string | null;
      created_at: string;
    }>;
  }> {
    return this.request(`/api/v1/dashboard/restaurant/upi/qr-code/history?limit=${limit}`, {
      method: 'GET',
    });
  }

  async revertQRCodeToVersion(version_number: number): Promise<RestaurantInfo> {
    return this.request<RestaurantInfo>(`/api/v1/dashboard/restaurant/upi/qr-code/revert/${version_number}`, {
      method: 'POST',
    });
  }

  // Settings API
  async getSettings(): Promise<SettingsResponse> {
    return this.request<SettingsResponse>('/api/v1/settings', {
      method: 'GET',
    });
  }

  async updateNotificationSettings(settings: NotificationSettings): Promise<SettingsResponse> {
    return this.request<SettingsResponse>('/api/v1/settings/notifications', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  async updateOrderSettings(settings: OrderSettings): Promise<SettingsResponse> {
    return this.request<SettingsResponse>('/api/v1/settings/orders', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  async sendTestNotification(): Promise<{ success: boolean; message: string; recipient: string }> {
    return this.request('/api/v1/settings/test-notification', {
      method: 'POST',
    });
  }

  async updateProfileSettings(profile: {
    restaurant_name: string;
    phone: string;
    address: string;
    latitude: number;
    longitude: number;
    delivery_radius_km?: number | null;
    gst_number?: string | null;
    pan_number?: string | null;
    fssai_number?: string | null;
    operating_hours?: Record<string, { open: string; close: string; closed: boolean }>;
  }): Promise<SettingsResponse> {
    return this.request<SettingsResponse>('/api/v1/settings/profile', {
      method: 'PUT',
      body: JSON.stringify(profile),
    });
  }

  async getCurrentUserProfile(): Promise<CurrentUserProfile> {
    return this.request<CurrentUserProfile>('/api/v1/auth/me', {
      method: 'GET',
    });
  }

  // Notifications API
  async getNotifications(event?: string, status?: string): Promise<Notification[]> {
    const params = new URLSearchParams();
    if (event) params.append('event', event);
    if (status) params.append('status', status);
    const query = params.toString();
    return this.request<Notification[]>(`/api/v1/notifications${query ? `?${query}` : ''}`, {
      method: 'GET',
    });
  }

  async getNotificationByOrder(orderId: string): Promise<Notification> {
    return this.request<Notification>(`/api/v1/notifications/order/${orderId}`, {
      method: 'GET',
    });
  }

  async getNotificationStats(): Promise<NotificationStats> {
    return this.request<NotificationStats>('/api/v1/notifications/stats', {
      method: 'GET',
    });
  }

  // Account Settings API
  async updateAccountSettings(settings: {
    owner_name: string;
    owner_email: string;
    current_password?: string;
    new_password?: string;
    two_factor_enabled: boolean;
  }): Promise<{
    message: string;
    user_id: string;
    owner_name: string;
    owner_email: string;
    two_factor_enabled: boolean;
  }> {
    return this.request('/api/v1/auth/account', {
      method: 'PUT',
      body: JSON.stringify(settings),
    });
  }

  // Public API (no authentication required) - for customers ordering via WhatsApp
  async getPublicMenu(restaurantId: string): Promise<{
    restaurant: {
      id: string;
      name: string;
      address: string;
      latitude?: number | null;
      longitude?: number | null;
      delivery_fee: number;
      upi_id: string;
      upi_qr_code?: string;  // QR code for payment page
      delivery_available?: boolean;  // Whether delivery option is available
    };
    categories: Array<{
      name: string;
      items: Array<{
        id: string;
        name: string;
        description: string;
        price: number;
        discounted_price?: number;
        discount_percentage?: number;
        is_available?: boolean;
      }>;
    }>;
  }> {
    // Public endpoint - no auth token needed
    const response = await fetch(`${API_BASE_URL}/api/public/menu/${restaurantId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch menu: ${response.statusText}`);
    }
    return response.json();
  }
}

// Export singleton instance
export const apiClient = new ApiClient();
