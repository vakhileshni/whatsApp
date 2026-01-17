# 💳 Payment System - How It Works

## Overview
This system uses **UPI (Unified Payments Interface)** for payments, which is the most popular payment method in India. The payment flow involves:
1. **Restaurant Setup** - Restaurant owner sets up their UPI ID and QR code
2. **Customer Payment** - Customer pays via UPI when placing order
3. **Payment Verification** - Restaurant verifies payment manually by matching customer's UPI name

---

## 🔧 Part 1: Restaurant Setup (One-Time)

### Step 1: Set Up UPI ID
**Location:** Dashboard → Click "UPI" button

1. **Enter UPI ID** (e.g., `restaurant@paytm` or `1234567890@upi`)
2. **Click "Verify UPI"**
3. **System generates a QR code** with ₹1 test payment
4. **Restaurant owner scans QR code** with their UPI app (PhonePe, GPay, Paytm)
5. **Makes ₹1 test payment** to verify the UPI ID works
6. **Enter verification code** from payment transaction
7. **UPI ID is saved** to database

### Step 2: Upload/Generate QR Code
**Location:** Settings → Payments Tab

**Option A: Upload QR Code Image**
- Click "Upload QR Code Image"
- Select your UPI QR code image (PNG/JPG)
- Image is converted to base64 and saved

**Option B: Generate QR Code**
- Click "Generate QR Code from UPI ID"
- System generates QR code using `qrserver.com` API
- QR code URL is saved

**Save:** Click "💾 Save QR Code" button
- QR code is saved to `restaurants.upi_qr_code` column
- **SCD Type 2** automatically creates history entry in `restaurant_upi_qr_code_history` table
- Every change is tracked with version numbers

---

## 💰 Part 2: Customer Payment Flow

### When Customer Places Order via WhatsApp:

1. **Customer sends order** via WhatsApp to restaurant's WhatsApp Business number
2. **System creates order** with status `pending` and `payment_status = 'pending'`
3. **WhatsApp message sent to customer** with:
   - Order confirmation
   - **UPI payment link** (e.g., `upi://pay?pa=restaurant@paytm&am=500&cu=INR`)
   - Instructions to pay

### Customer Payment Options:

**Option A: Click UPI Link (Recommended)**
- Customer clicks the UPI link in WhatsApp
- UPI app opens automatically (PhonePe, GPay, Paytm)
- Customer enters UPI PIN
- Payment is completed

**Option B: Scan QR Code**
- Customer goes to Dashboard → Clicks "UPI" button
- QR code modal opens showing restaurant's QR code
- Customer scans with UPI app
- Payment is completed

---

## ✅ Part 3: Payment Verification (Restaurant Side)

### How Restaurant Verifies Payment:

**Location:** Dashboard → Orders → Click on Order Card

1. **Customer makes payment** via UPI
2. **Restaurant receives payment notification** on their phone (from their bank/UPI app)
3. **Payment notification shows:**
   - Customer's UPI name (e.g., "RAJESH KUMAR", "PRIYA S", etc.)
   - Amount paid
   - Transaction ID

4. **Restaurant opens order details** on Dashboard
5. **Clicks "Verify Payment" button**
6. **Enters customer's UPI name** from payment notification
7. **Clicks "Confirm"**
8. **System updates order:**
   - `payment_status = 'verified'`
   - `customer_upi_name = <entered name>`
   - Order status can now be updated to `preparing`

### Payment Status States:

- **⏳ Pending** - Payment not yet verified (yellow badge)
- **✓ Verified** - Payment confirmed by restaurant (green badge)
- **✕ Failed** - Payment failed or cancelled (red badge)

---

## 📊 Database Structure

### Tables Involved:

1. **`restaurants` table:**
   - `upi_id` - Restaurant's UPI ID (e.g., `restaurant@paytm`)
   - `upi_qr_code` - Current QR code (base64 or URL)
   - `upi_password` - Optional password for UPI management

2. **`restaurant_upi_qr_code_history` table (SCD Type 2):**
   - Tracks all QR code changes
   - `version_number` - Sequential version (1, 2, 3...)
   - `is_current` - TRUE for latest version
   - `effective_from` / `effective_to` - When version was active
   - Full audit trail of all QR code changes

3. **`orders` table:**
   - `payment_status` - `pending`, `verified`, `failed`
   - `customer_upi_name` - Customer's UPI name from payment notification
   - `payment_method` - Usually `'upi'`

---

## 🔄 Complete Payment Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    RESTAURANT SETUP                          │
└─────────────────────────────────────────────────────────────┘
         │
         ├─→ Set UPI ID (Dashboard → UPI button)
         │   └─→ Verify with ₹1 test payment
         │
         └─→ Upload/Generate QR Code (Settings → Payments)
             └─→ Save QR Code → Database
                 └─→ SCD History Created

┌─────────────────────────────────────────────────────────────┐
│                    CUSTOMER ORDER                           │
└─────────────────────────────────────────────────────────────┘
         │
         ├─→ Customer orders via WhatsApp
         │
         ├─→ System creates order (payment_status = 'pending')
         │
         └─→ WhatsApp message sent with UPI payment link
             │
             ├─→ Customer clicks link → UPI app opens
             │   └─→ Customer pays ₹500
             │
             └─→ OR Customer scans QR code from Dashboard
                 └─→ Customer pays ₹500

┌─────────────────────────────────────────────────────────────┐
│                 PAYMENT VERIFICATION                         │
└─────────────────────────────────────────────────────────────┘
         │
         ├─→ Restaurant receives payment notification
         │   └─→ Shows: "RAJESH KUMAR paid ₹500"
         │
         ├─→ Restaurant opens Dashboard → Order Details
         │
         ├─→ Clicks "Verify Payment" button
         │
         ├─→ Enters customer UPI name: "RAJESH KUMAR"
         │
         └─→ Clicks "Confirm"
             └─→ Order updated: payment_status = 'verified'
                 └─→ Order can now be processed
```

---

## 🎯 Key Features

### 1. **QR Code Management**
- Upload custom QR code image
- Generate QR code from UPI ID
- Version history tracking (SCD Type 2)
- Revert to previous versions

### 2. **Payment Verification**
- Manual verification by restaurant owner
- Matches customer UPI name from payment notification
- Prevents fraud by requiring verification

### 3. **Payment Status Tracking**
- Real-time status updates
- Visual indicators (green/yellow/red badges)
- Customer UPI name stored for records

### 4. **WhatsApp Integration**
- Automatic UPI payment links sent to customers
- QR code display on dashboard
- Payment reminders

---

## 🔒 Security Features

1. **UPI Password Protection**
   - Optional password for UPI management
   - Separate from login password

2. **Payment Verification**
   - Requires manual verification
   - Customer UPI name must match payment notification

3. **SCD Type 2 History**
   - Complete audit trail
   - Can revert to previous QR codes
   - Tracks who changed what and when

---

## 📱 User Interface Locations

### Restaurant Dashboard:
- **UPI Button** (Top right) → Set/Verify UPI ID, View QR Code
- **Orders Tab** → View orders, Verify payments
- **Settings → Payments Tab** → Manage QR Code

### Customer Experience:
- **WhatsApp** → Receives order confirmation + UPI payment link
- **Dashboard QR Code** → Can scan QR code to pay

---

## 🚀 Future Enhancements (Possible)

1. **Automatic Payment Verification**
   - Integration with payment gateway APIs
   - Auto-verify payments using transaction IDs

2. **Payment Gateway Integration**
   - Razorpay, Paytm Gateway
   - Automatic payment status updates

3. **Payment Analytics**
   - Track payment success rates
   - Average payment time
   - Failed payment reasons

---

## ❓ Common Questions

**Q: Why manual verification?**
A: UPI doesn't provide webhook callbacks by default. Manual verification ensures accuracy and prevents fraud.

**Q: What if customer pays but doesn't match UPI name?**
A: Restaurant can still verify by checking transaction ID or amount. UPI name is just one verification method.

**Q: Can I change QR code after saving?**
A: Yes! Upload new QR code and save. Old version is kept in history table.

**Q: What happens if payment fails?**
A: Order remains in `pending` status. Restaurant can mark as `failed` or wait for retry.

---

## 📝 Summary

The payment system is designed for **Indian market** using **UPI**, which is:
- ✅ Most popular payment method in India
- ✅ Works with all UPI apps (PhonePe, GPay, Paytm, etc.)
- ✅ No additional payment gateway fees
- ✅ Instant payments
- ✅ Secure and reliable

The system provides:
- ✅ Easy setup for restaurants
- ✅ Simple payment flow for customers
- ✅ Manual verification for security
- ✅ Complete payment history tracking
