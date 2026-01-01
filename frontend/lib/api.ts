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
  customer_rating?: number;  // Rating given by customer (1-5)
  total_amount?: number;  // Alias for total
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
  upi_id: string;
  twilio_number: string;  // WhatsApp Business number for QR codes
  is_active: boolean;  // Restaurant open/closed status
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
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    // Add auth token if required
    if (requireAuth) {
      const token = getToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    const response = await fetch(url, {
      ...options,
      headers,
    });

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

  async confirmUPIVerification(verification_code: string, upi_id: string, password: string, new_password?: string): Promise<RestaurantInfo> {
    return this.request<RestaurantInfo>('/api/v1/dashboard/restaurant/upi/confirm-verification', {
      method: 'POST',
      body: JSON.stringify({ 
        verification_code,
        upi_id, 
        password,
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

  async verifyPayment(orderId: string, customer_upi_name: string): Promise<Order> {
    return this.request<Order>(`/api/v1/orders/${orderId}/verify-payment`, {
      method: 'PATCH',
      body: JSON.stringify({ customer_upi_name }),
    });
  }

  async verifyRestaurantUPI(upi_id: string, password: string): Promise<VerifyUPIResponse> {
    return this.request<VerifyUPIResponse>('/api/v1/dashboard/restaurant/upi/verify', {
      method: 'POST',
      body: JSON.stringify({ upi_id, password }),
    });
  }

  // Public API (no authentication required) - for customers ordering via WhatsApp
  async getPublicMenu(restaurantId: string): Promise<{
    restaurant: {
      id: string;
      name: string;
      address: string;
      delivery_fee: number;
      upi_id: string;
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
