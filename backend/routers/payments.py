"""
Payment Router - Razorpay webhook and payment endpoints
"""
from fastapi import APIRouter, HTTPException, Request, Header
from pydantic import BaseModel
from typing import Optional
import logging
import json

from services.payment_service import verify_razorpay_webhook_signature, get_payment_status
from repositories.order_repo import get_order_by_id, update_order
from services.whatsapp_service import send_whatsapp_message, format_phone_number
from repositories.restaurant_repo import get_restaurant_by_id
from datetime import datetime

router = APIRouter(prefix="/api/v1/payments", tags=["payments"])
logger = logging.getLogger(__name__)


@router.post("/razorpay/webhook")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: Optional[str] = Header(None, alias="X-Razorpay-Signature")
):
    """
    Razorpay webhook endpoint for automatic payment verification
    This is called automatically by Razorpay when payment is made
    """
    try:
        # Get raw request body
        body = await request.body()
        body_str = body.decode('utf-8')
        webhook_data = json.loads(body_str)
        
        logger.info(f"📥 Received Razorpay webhook: {webhook_data.get('event')}")
        
        # Verify webhook signature
        if x_razorpay_signature:
            if not verify_razorpay_webhook_signature(body_str, x_razorpay_signature):
                logger.error("❌ Invalid webhook signature")
                raise HTTPException(status_code=400, detail="Invalid webhook signature")
        
        # Handle payment.paid event
        if webhook_data.get("event") == "payment_link.paid":
            payment_link_data = webhook_data.get("payload", {}).get("payment_link", {}).get("entity", {})
            payment_link_id = payment_link_data.get("id")
            order_id = payment_link_data.get("notes", {}).get("order_id")
            
            if not order_id:
                logger.error("❌ Order ID not found in webhook payload")
                raise HTTPException(status_code=400, detail="Order ID not found")
            
            logger.info(f"✅ Payment received for order {order_id}, payment link: {payment_link_id}")
            
            # Get order
            order = get_order_by_id(order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                raise HTTPException(status_code=404, detail="Order not found")
            
            # Update order payment status
            order.payment_status = "verified"
            order.updated_at = datetime.now().isoformat()
            
            # Save updated order
            updated_order = update_order(order)
            
            if not updated_order:
                logger.error(f"Failed to update order {order_id}")
                raise HTTPException(status_code=500, detail="Failed to update order")
            
            # Send WhatsApp confirmation to customer
            try:
                customer_phone = format_phone_number(order.customer_phone)
                confirmation_message = (
                    f"✅ *Payment Confirmed!*\n\n"
                    f"Hi {order.customer_name}!\n\n"
                    f"Payment of ₹{order.total_amount:.0f} for order *#{order.id[:8]}* has been confirmed.\n\n"
                    f"Your order is now being processed! 🍽️\n\n"
                    f"We'll notify you when we start preparing your order."
                )
                await send_whatsapp_message(customer_phone, confirmation_message)
                logger.info(f"✅ Payment confirmation sent to {customer_phone} for order {order.id}")
            except Exception as e:
                logger.error(f"❌ Failed to send payment confirmation: {e}")
            
            # Send notification to restaurant owner
            try:
                from services.whatsapp_service import send_restaurant_order_notification
                await send_restaurant_order_notification(updated_order, "payment_received")
            except Exception as e:
                logger.error(f"❌ Failed to send restaurant notification: {e}")
            
            return {"status": "success", "message": "Payment verified and order updated"}
        
        # Handle other events (payment failed, etc.)
        elif webhook_data.get("event") == "payment_link.cancelled":
            payment_link_data = webhook_data.get("payload", {}).get("payment_link", {}).get("entity", {})
            order_id = payment_link_data.get("notes", {}).get("order_id")
            
            if order_id:
                order = get_order_by_id(order_id)
                if order:
                    order.payment_status = "failed"
                    order.updated_at = datetime.now().isoformat()
                    update_order(order)
                    logger.info(f"Payment cancelled for order {order_id}")
        
        return {"status": "received"}
        
    except Exception as e:
        logger.error(f"❌ Error processing Razorpay webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


@router.get("/status/{payment_link_id}")
async def get_payment_link_status(payment_link_id: str):
    """
    Get payment status for a Razorpay payment link
    Used by frontend to poll payment status
    """
    try:
        payment_status = get_payment_status(payment_link_id)
        
        if not payment_status:
            raise HTTPException(status_code=404, detail="Payment link not found")
        
        # Extract order ID from notes
        order_id = payment_status.get("notes", {}).get("order_id")
        
        return {
            "payment_link_id": payment_link_id,
            "status": payment_status.get("status"),  # "created", "paid", "cancelled", etc.
            "amount": payment_status.get("amount") / 100 if payment_status.get("amount") else 0,  # Convert from paise
            "order_id": order_id,
            "paid_at": payment_status.get("paid_at")
        }
    except Exception as e:
        logger.error(f"❌ Error fetching payment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
