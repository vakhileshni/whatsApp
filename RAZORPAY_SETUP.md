# Razorpay Payment Gateway Setup Guide

## Overview

The system now supports **automatic payment verification** using Razorpay payment gateway. This means customers don't need to manually verify payments - the system automatically detects when payment is made!

## How It Works

1. **Customer places order** with online payment
2. **System creates Razorpay payment link** (if configured) or falls back to UPI QR code
3. **Customer pays** via Razorpay link or QR code
4. **Razorpay sends webhook** to backend when payment is made
5. **Backend automatically verifies** payment and updates order status
6. **Customer receives WhatsApp confirmation** automatically
7. **Payment page updates automatically** (no manual verification needed!)

## Setup Instructions

### Step 1: Create Razorpay Account

1. Go to https://razorpay.com
2. Sign up for a free account
3. Complete KYC verification (required for live payments)

### Step 2: Get API Keys

1. Go to **Settings** → **API Keys** in Razorpay Dashboard
2. Generate **Test Keys** (for development) or **Live Keys** (for production)
3. Copy your **Key ID** and **Key Secret**

### Step 3: Configure Webhook

1. Go to **Settings** → **Webhooks** in Razorpay Dashboard
2. Click **Add New Webhook**
3. Set webhook URL: `https://your-domain.com/api/v1/payments/razorpay/webhook`
   - For local development, use ngrok: `https://your-ngrok-url.ngrok-free.app/api/v1/payments/razorpay/webhook`
4. Select events to listen for:
   - ✅ `payment_link.paid` (required)
   - ✅ `payment_link.cancelled` (optional)
5. Copy the **Webhook Secret** (shown after creating webhook)

### Step 4: Add Environment Variables

Add these to your `.env` file in the `backend` directory:

```env
# Razorpay Payment Gateway Configuration
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=your_key_secret_here
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret_here
```

### Step 5: Restart Backend

Restart your backend server to load the new environment variables.

## Testing

### Test Mode (Development)

1. Use **Test Keys** from Razorpay Dashboard
2. Use Razorpay test cards: https://razorpay.com/docs/payments/test-cards/
3. Test payment flow:
   - Place an order with online payment
   - Click "Pay Now" or scan QR code
   - Complete payment using test card
   - Payment should be automatically verified!

### Live Mode (Production)

1. Use **Live Keys** from Razorpay Dashboard
2. Ensure webhook URL is publicly accessible
3. Test with real payments (small amounts)

## Fallback Behavior

If Razorpay is **not configured**:
- System automatically falls back to **UPI QR code** method
- Customers can still pay via QR code
- Manual verification form is shown (as before)

## Benefits

✅ **Automatic Verification** - No manual steps for customers  
✅ **Real-time Updates** - Payment page updates automatically  
✅ **WhatsApp Notifications** - Automatic confirmation messages  
✅ **Secure** - Webhook signature verification  
✅ **Multiple Payment Methods** - Cards, UPI, Wallets, Net Banking  
✅ **Payment Analytics** - Track payment success rates  

## Troubleshooting

### Payment Not Being Verified

1. **Check webhook URL**: Ensure it's publicly accessible
2. **Check webhook logs**: Go to Razorpay Dashboard → Webhooks → View Logs
3. **Check backend logs**: Look for webhook errors
4. **Verify webhook secret**: Ensure it matches in `.env` file

### Webhook Not Receiving Events

1. **Test webhook**: Use Razorpay's webhook testing tool
2. **Check firewall**: Ensure webhook endpoint is accessible
3. **Check ngrok**: If using ngrok, ensure tunnel is active
4. **Verify events**: Ensure `payment_link.paid` event is selected

### Payment Link Not Created

1. **Check API keys**: Verify `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`
2. **Check backend logs**: Look for Razorpay initialization errors
3. **Verify account status**: Ensure Razorpay account is active

## Support

- Razorpay Documentation: https://razorpay.com/docs/
- Razorpay Support: support@razorpay.com
- Payment Link API: https://razorpay.com/docs/api/payment-links/

## Notes

- **Test Mode**: No real money is charged, perfect for development
- **Live Mode**: Real payments are processed, requires KYC verification
- **Fees**: Razorpay charges ~2% per transaction (standard for payment gateways)
- **Refunds**: Can be processed through Razorpay Dashboard
