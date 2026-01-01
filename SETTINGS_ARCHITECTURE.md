# Restaurant Dashboard Settings - Architecture Document

## Overview
Comprehensive settings page for restaurant owners to manage notifications, subscriptions, profile, and system preferences.

## Settings Page Structure

### 1. **Notifications Settings** 🔔
- **WhatsApp Notifications**
  - Enable/Disable WhatsApp notifications for new orders
  - WhatsApp number display (read-only, from restaurant profile)
  - Test notification button
  - Notification frequency (Instant, Batch every 5 min, Batch every 15 min)
  
- **Email Notifications**
  - Enable/Disable email notifications
  - Email address input/verification
  - Notification preferences (New orders, Order updates, Daily summary, Weekly report)
  
- **SMS Notifications** (Optional)
  - Enable/Disable SMS notifications
  - Phone number for SMS
  
- **Order Status Notifications**
  - Checkboxes for each status:
    - ✅ New Order (Pending)
    - ✅ Order Preparing
    - ✅ Order Ready
    - ✅ Order Delivered
    - ✅ Order Cancelled
    - ✅ Payment Received
  
- **Sound & Visual Alerts**
  - Enable/Disable sound notifications (already exists)
  - Enable/Disable blinking animations
  - Sound volume control

### 2. **Subscription Management** 💳
- **Current Plan Display**
  - Plan name (Free, Basic, Pro, Enterprise)
  - Plan features list
  - Monthly/Annual billing cycle
  - Current status (Active, Expired, Trial, Cancelled)
  
- **Subscription Details**
  - Subscription start date
  - Next billing date
  - Auto-renewal status (On/Off)
  - Subscription expiry date
  
- **Plan Features Comparison**
  - Table showing features across plans
  - Current plan highlighted
  
- **Upgrade/Downgrade Options**
  - Button to view all plans
  - Upgrade button (if on lower plan)
  - Downgrade option (if on higher plan)
  
- **Billing Information**
  - Billing address
  - Payment method (Card, UPI, Bank Transfer)
  - Tax information (GST number)
  
- **Payment History**
  - Table of past payments
  - Invoice download
  - Payment status
  - Amount and date
  
- **Subscription Actions**
  - Cancel subscription
  - Reactivate subscription
  - Change billing cycle

### 3. **Restaurant Profile Settings** 🏪
- **Basic Information**
  - Restaurant name (editable)
  - Restaurant description/bio
  - Restaurant logo upload
  - Cover image upload
  
- **Contact Information**
  - Phone number (primary)
  - Alternate phone number
  - Email address
  - Website URL
  
- **Location Settings**
  - Restaurant address (editable)
  - Latitude/Longitude (auto-update on address change)
  - Delivery radius (km)
  - Service areas (multiple locations)
  
- **Operating Hours**
  - Day-wise hours (Monday-Sunday)
  - Open/Close times
  - Special hours (holidays, events)
  - Timezone selection
  
- **Business Details**
  - GST number
  - PAN number
  - FSSAI license number
  - Business registration number

### 4. **Account Settings** 👤
- **Security**
  - Change password
  - Two-factor authentication (2FA) enable/disable
  - Login history
  - Active sessions management
  
- **Profile**
  - Owner name
  - Owner email
  - Owner phone number
  - Profile picture
  
- **Privacy**
  - Data sharing preferences
  - Analytics opt-in/opt-out
  - Marketing communications
  
- **Account Management**
  - Deactivate account (temporary)
  - Delete account (permanent)
  - Export data (GDPR compliance)

### 5. **Order Settings** 📦
- **Order Management**
  - Auto-accept orders (Yes/No)
  - Auto-print orders (Yes/No)
  - Default preparation time (minutes)
  - Maximum order value
  - Minimum order value
  
- **Order Processing**
  - Order confirmation required (Yes/No)
  - Allow order modifications (Yes/No)
  - Order cancellation policy
  - Refund policy
  
- **Delivery Settings**
  - Delivery charge calculation (Fixed, Distance-based, Order value-based)
  - Free delivery threshold
  - Delivery time slots
  - Delivery partner integration

### 6. **Payment Settings** 💰
- **Payment Methods**
  - UPI (already exists)
  - Cash on Delivery (enable/disable)
  - Online payment (enable/disable)
  - Payment gateway settings
  
- **Payment Processing**
  - Payment verification method
  - Auto-verify payment (Yes/No)
  - Payment reminder settings

### 7. **Display & Preferences** 🎨
- **Theme Settings**
  - Light/Dark mode toggle
  - Color scheme selection
  
- **Language & Region**
  - Language selection (English, Hindi, etc.)
  - Date format
  - Time format (12h/24h)
  - Currency display
  
- **Dashboard Preferences**
  - Default view (Orders/Menu)
  - Items per page
  - Auto-refresh interval
  - Notification position

### 8. **Integration Settings** 🔌
- **WhatsApp Business API**
  - API credentials
  - Webhook URL
  - Message templates
  
- **Third-party Integrations**
  - POS system integration
  - Accounting software
  - Delivery partner APIs
  - Analytics tools

### 9. **Advanced Settings** ⚙️
- **API Management**
  - API keys generation
  - API usage statistics
  - Webhook endpoints
  
- **Data & Backup**
  - Data export
  - Backup schedule
  - Restore from backup
  
- **System Settings**
  - Cache management
  - Log retention period
  - Performance optimization

## Backend Requirements

### Database Models Needed:
1. **RestaurantSettings**
   - restaurant_id (FK)
   - whatsapp_notifications_enabled (boolean)
   - email_notifications_enabled (boolean)
   - sms_notifications_enabled (boolean)
   - notification_preferences (JSON)
   - order_auto_accept (boolean)
   - default_preparation_time (integer)
   - delivery_radius (float)
   - operating_hours (JSON)
   - theme_preference (string)
   - language (string)
   - timezone (string)

2. **Subscription**
   - restaurant_id (FK)
   - plan_name (string)
   - plan_type (enum: free, basic, pro, enterprise)
   - status (enum: active, expired, trial, cancelled)
   - start_date (datetime)
   - expiry_date (datetime)
   - billing_cycle (enum: monthly, annual)
   - auto_renewal (boolean)
   - payment_method (string)
   - billing_address (JSON)

3. **PaymentHistory**
   - subscription_id (FK)
   - amount (decimal)
   - payment_date (datetime)
   - payment_method (string)
   - transaction_id (string)
   - invoice_url (string)
   - status (enum: success, failed, pending)

### API Endpoints Needed:
- `GET /api/v1/settings` - Get all settings
- `PUT /api/v1/settings/notifications` - Update notification settings
- `PUT /api/v1/settings/profile` - Update restaurant profile
- `PUT /api/v1/settings/account` - Update account settings
- `PUT /api/v1/settings/orders` - Update order settings
- `GET /api/v1/subscription` - Get subscription details
- `POST /api/v1/subscription/upgrade` - Upgrade subscription
- `POST /api/v1/subscription/cancel` - Cancel subscription
- `GET /api/v1/subscription/payments` - Get payment history

## UI/UX Design

### Layout:
- Tabbed interface with sidebar navigation
- Each section in a card layout
- Save button at bottom of each section
- Success/Error toast notifications
- Loading states for async operations

### Color Scheme:
- Primary: Blue/Indigo (existing)
- Success: Green
- Warning: Yellow/Orange
- Danger: Red
- Info: Blue

### Responsive Design:
- Mobile-first approach
- Collapsible sections on mobile
- Touch-friendly buttons
- Optimized for tablet and desktop

## Implementation Priority

### Phase 1 (MVP):
1. Settings button in header
2. Settings page structure
3. Notifications settings (WhatsApp focus)
4. Basic subscription display

### Phase 2:
1. Restaurant profile settings
2. Account settings
3. Order settings
4. Full subscription management

### Phase 3:
1. Advanced integrations
2. API management
3. Data export/backup
4. Analytics and reporting

