<<<<<<< HEAD
# Multi-Tenant WhatsApp Ordering SaaS

A complete multi-tenant WhatsApp Ordering SaaS for restaurants built with **Next.js** frontend and **FastAPI** Python backend.

## 🎯 Features

- ✅ **Multi-tenant architecture** - Multiple restaurants with complete data isolation
- ✅ **JWT Authentication** - Secure restaurant admin login
- ✅ **Order Management** - View, update order status (Pending → Preparing → Ready → Delivered)
- ✅ **Menu Management** - View and manage menu items
- ✅ **WhatsApp Webhook** - Ready for Twilio WhatsApp integration
- ✅ **Dashboard Statistics** - Real-time stats (orders, revenue, etc.)
- ✅ **Hardcoded Demo Data** - No external database required for testing

## 🏗️ Tech Stack

- **Frontend**: Next.js 16 (React 19) + TypeScript + Tailwind CSS
- **Backend**: FastAPI (Python) + JWT Authentication
- **WhatsApp**: Twilio WhatsApp Business API (webhook ready)
- **Data Storage**: In-memory (hardcoded demo data in `backend/data.py`)

## 📁 Project Structure

```
.
├── frontend/              # Next.js frontend application
│   ├── app/
│   │   ├── login/        # Login page
│   │   ├── dashboard/    # Main dashboard (orders + menu)
│   │   └── page.tsx      # Home (redirects to login/dashboard)
│   ├── lib/
│   │   └── api.ts        # API client with JWT auth
│   └── package.json
│
└── backend/              # FastAPI Python backend
    ├── main.py           # FastAPI app + all endpoints
    ├── auth.py           # JWT authentication utilities
    ├── data.py           # Hardcoded demo data (restaurants, users, products)
    └── requirements.txt  # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- Python 3.8+ 
- Node.js 18+ and npm
- (Optional) Virtual environment for Python

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the backend server:**
```bash
python main.py
```

Backend will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Run the development server:**
```bash
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🔐 Demo Credentials

The system comes with hardcoded demo data. Use these credentials to login:

### Restaurant 1: Spice Garden
- **Email**: `admin@spicegarden.com`
- **Password**: `admin123`
- **Restaurant ID**: `rest_001`

### Restaurant 2: Pizza Paradise
- **Email**: `admin@pizzaparadise.com`
- **Password**: `admin123`
- **Restaurant ID**: `rest_002`

## 📊 Demo Data

The system includes:

- **2 Restaurants**: Spice Garden & Pizza Paradise
- **2 Admin Users**: One for each restaurant
- **12 Products**: 6 items per restaurant
  - Spice Garden: Butter Chicken, Biryani, Paneer Tikka, Naan, Dal Makhani, Gulab Jamun
  - Pizza Paradise: Margherita Pizza, Pepperoni Pizza, Veg Supreme, Garlic Bread, Caesar Salad, Chocolate Brownie

All data is stored in `backend/data.py` - no external database required!

## 🔌 API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Restaurant admin login

### Orders
- `GET /api/v1/orders` - Get all orders (restaurant-scoped)
- `GET /api/v1/orders/{order_id}` - Get specific order
- `POST /api/v1/orders` - Create new order
- `PATCH /api/v1/orders/{order_id}/status` - Update order status

### Menu
- `GET /api/v1/menu` - Get all menu items (restaurant-scoped)
- `POST /api/v1/menu` - Create new menu item
- `PUT /api/v1/menu/{product_id}` - Update menu item

### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard statistics

### Webhook
- `POST /api/v1/webhook/whatsapp` - WhatsApp webhook handler (Twilio)

## 🎨 Frontend Features

### Login Page (`/login`)
- Email/password authentication
- JWT token storage in localStorage
- Auto-redirect to dashboard on success

### Dashboard Page (`/dashboard`)
- **Overview Stats**: Total orders, pending orders, today's orders, total revenue
- **Orders Tab**: 
  - View all orders with status badges
  - Update order status (Pending → Preparing → Ready → Delivered)
  - View order details (items, customer info, delivery address)
  - Filter by status
- **Menu Tab**:
  - View all menu items
  - Toggle item availability
  - View product details (price, category, description)

## 🔒 Multi-Tenant Security

- **JWT Authentication**: Each restaurant admin gets a JWT token with `restaurant_id`
- **Data Isolation**: All API endpoints automatically filter by `restaurant_id` from JWT
- **Authorization**: Users can only access their own restaurant's data
- **Middleware**: `get_current_restaurant_id()` dependency ensures tenant isolation

## 📱 WhatsApp Integration (Ready)

The backend includes a WhatsApp webhook endpoint at `/api/v1/webhook/whatsapp` that accepts Twilio webhook format:

```python
{
  "From": "whatsapp:+1234567890",
  "To": "whatsapp:+0987654321",
  "Body": "Hello, I want to order",
  "MessageSid": "..."
}
```

To integrate:
1. Set up Twilio WhatsApp Business API
2. Configure webhook URL: `https://your-domain.com/api/v1/webhook/whatsapp`
3. Implement bot logic in the webhook handler (currently just acknowledges receipt)

## 🧪 Testing the System

1. **Start both servers:**
   - Backend: `cd backend && python main.py`
   - Frontend: `cd frontend && npm run dev`

2. **Login:**
   - Go to http://localhost:3000
   - Use demo credentials (e.g., `admin@spicegarden.com` / `admin123`)

3. **View Dashboard:**
   - See stats and menu items
   - Orders will appear when created (via API or webhook)

4. **Test API directly:**
   - Visit http://localhost:8000/docs
   - Use "Authorize" button to add JWT token
   - Test endpoints interactively

## 🚢 Production Considerations

For production deployment:

1. **Database**: Replace hardcoded data with PostgreSQL/MySQL
2. **Password Hashing**: Use `bcrypt` or similar (currently plain text)
3. **JWT Secret**: Store in environment variable (currently hardcoded)
4. **CORS**: Update allowed origins for production domain
5. **Error Handling**: Add comprehensive error logging
6. **Rate Limiting**: Add rate limiting for API endpoints
7. **WhatsApp Bot**: Implement full bot logic for order flow

## 📝 Notes

- All data is stored in memory and will be lost on server restart
- Passwords are stored in plain text (for demo only)
- JWT secret is hardcoded (change for production)
- WhatsApp webhook handler is a stub (ready for implementation)

## 🤝 Development

To add more demo data, edit `backend/data.py`:

- Add restaurants to `RESTAURANTS` dict
- Add users to `USERS` dict
- Add products to `PRODUCTS` dict

All data is automatically scoped by `restaurant_id` for multi-tenant isolation.

## 📚 Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Twilio WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [JWT Authentication](https://jwt.io/)

---

**Built with ❤️ for restaurant owners**
=======
# whatsApp
>>>>>>> b6e6f12fc106cdf7a68639a5a666c0bae636bcae
