# Android App Integration Guide

## Restaurant App (android-app)

### Completed
✅ API Service updated with all backend endpoints
✅ Settings Repository created
✅ Notification Repository created
✅ Settings ViewModel created
✅ Dependency Injection updated

### Remaining Tasks

1. **Settings Screen** - Create comprehensive settings screen with tabs:
   - Profile Settings (restaurant name, phone, address, location, business details)
   - Notification Settings (WhatsApp, email, SMS notifications)
   - Order Settings (auto-accept, preparation time, delivery availability)
   - Account Settings (owner info, password change, MFA)

2. **Dashboard Screen Updates**:
   - Add stats cards (total orders, pending, revenue)
   - Add menu management
   - Add order filtering and management
   - Add settings navigation

3. **Navigation Updates**:
   - Add Settings screen to navigation
   - Add proper bottom navigation

4. **Missing Models**:
   - RestaurantInfoResponse model
   - ProductCreate/ProductUpdate models
   - PublicMenuResponse model

## Delivery Person App (delivery-app)

### Structure Created
✅ Backend delivery router created
✅ Basic app structure defined

### Implementation Needed

1. **Data Models**:
   - DeliveryPerson model
   - DeliveryOrder model
   - Location model

2. **Network Layer**:
   - ApiService with delivery endpoints
   - RetrofitClient setup

3. **Repositories**:
   - DeliveryRepository
   - LocationRepository

4. **ViewModels**:
   - AuthViewModel (for delivery person login/signup)
   - DeliveryViewModel (for orders and availability)
   - LocationViewModel (for location tracking)

5. **Screens**:
   - LoginScreen
   - SignUpScreen
   - HomeScreen (with availability toggle and map)
   - OrdersScreen (list of available delivery orders)
   - OrderDetailScreen (order details and navigation)
   - ProfileScreen

6. **Features**:
   - Live location tracking with background service
   - Push notifications for new orders
   - Map integration for navigation
   - Availability toggle
   - Order acceptance and completion

## Backend Endpoints Status

### Delivery Endpoints (Created but need implementation):
- ✅ `/api/v1/delivery/signup` - Structure created
- ✅ `/api/v1/delivery/login` - Structure created
- ✅ `/api/v1/delivery/availability` - Structure created
- ✅ `/api/v1/delivery/location` - Structure created
- ✅ `/api/v1/delivery/orders` - Basic implementation (returns ready delivery orders)
- ✅ `/api/v1/delivery/orders/{order_id}/accept` - Structure created
- ✅ `/api/v1/delivery/orders/{order_id}/complete` - Implementation done

### Database Schema Needed:
- `delivery_persons` table with:
  - id, name, phone, email, password_hash
  - vehicle_type, license_number
  - is_available, current_latitude, current_longitude
  - created_at, updated_at

- `delivery_assignments` table (optional):
  - id, delivery_person_id, order_id
  - assigned_at, completed_at, status

## Next Steps

1. Complete Settings screen in restaurant app
2. Implement delivery person database models and authentication
3. Complete delivery person Android app
4. Add WebSocket or polling for real-time order notifications
5. Add background location service for delivery app
