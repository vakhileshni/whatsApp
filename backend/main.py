"""
Main FastAPI Application
WhatsApp Business Ordering System Backend
"""
import logging
import os
import time
from fastapi import FastAPI, Form, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse, Response, HTMLResponse
from twilio.twiml.messaging_response import MessagingResponse
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, dashboard, menu, orders, webhook
from typing import Optional
from datetime import datetime, timedelta
from repositories.session_repo import get_session, get_session_by_phone, create_session, update_session
from repositories.restaurant_repo import find_restaurants_by_location, get_restaurant_by_id
from repositories.product_repo import get_products_by_restaurant
from repositories.customer_repo import get_customer_by_phone, create_customer
from models.session import CustomerSession
from models.customer import Customer
from models.order import Order, OrderItem
from services.order_service import create_new_order
from services.whatsapp_service import send_order_status_notification
import uuid
import urllib.parse

# Twilio credentials (HARDCODED)
TWILIO_ACCOUNT_SID = "AC86fcf2e736ee575dc4403337c0ffc5da"
TWILIO_AUTH_TOKEN = "f09de2609a6290b8d641ea91065c8050"

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app instance
app = FastAPI(
    title="WhatsApp Business Ordering System",
    description="Backend API for WhatsApp Business ordering system",
    version="1.0.0"
)

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(menu.router)
app.include_router(orders.router)
app.include_router(webhook.router)

@app.get("/")
async def root():
    """Root endpoint - health check"""
    logger.info("Root endpoint accessed")
    return {
        "status": "ok",
        "message": "WhatsApp Business Ordering System API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("startup")
async def startup_event():
    """Log startup information"""
    logger.info("🚀 WhatsApp Business Ordering System API started")
    logger.info("📱 Webhook endpoint: /whatsapp")

# -------------------------------
# Twilio WhatsApp Webhook Endpoint
# -------------------------------
@app.post("/whatsapp", response_class=PlainTextResponse)
async def whatsapp_reply(
    From: str = Form(...), 
    Body: Optional[str] = Form(None),
    Latitude: Optional[str] = Form(None),
    Longitude: Optional[str] = Form(None),
    ProfileName: Optional[str] = Form(None)  # Customer name from WhatsApp
):
    """
    Endpoint to receive incoming WhatsApp messages from Twilio.
    Handles location-based restaurant selection flow:
    1. First message -> Ask for location
    2. Location shared -> Show nearest restaurants
    3. Restaurant selected -> Show menu
    """
    # Normalize phone number (remove whatsapp: prefix if present)
    phone_number = From.replace("whatsapp:", "").strip()
    customer_name = ProfileName or "Customer"  # Get name from WhatsApp profile

    response = MessagingResponse()
    
    # Get or create customer session
    # Use get_session_by_phone to find existing session regardless of restaurant_id
    session = get_session_by_phone(phone_number)
    
    # Handle location sharing (Latitude and Longitude are provided by Twilio when user shares location)
    if Latitude and Longitude:
        try:
            latitude = float(Latitude)
            longitude = float(Longitude)
            logger.info(f"📍 Location received from {phone_number}: lat={latitude}, lon={longitude}")
            
            # Check if this is QR code flow (restaurant already selected)
            is_qr_flow = session and session.restaurant_id and session.current_step in ["qr_location_request", "qr_location_confirm"]
            
            if is_qr_flow:
                # QR code flow - redirect directly to menu
                restaurant = get_restaurant_by_id(session.restaurant_id)
                if restaurant and restaurant.is_active:
                    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
                    customer_name_param = urllib.parse.quote(session.customer_name or customer_name or "Customer", safe='')
                    menu_link = f"{frontend_url}/menu/{session.restaurant_id}?token={urllib.parse.quote(phone_number, safe='')}&lat={latitude}&lon={longitude}&name={customer_name_param}"
                    
                    # Update session with location
                    location_timestamp = datetime.now().isoformat()
                    session.latitude = latitude
                    session.longitude = longitude
                    session.location_timestamp = location_timestamp
                    session.current_step = "menu"
                    if not session.customer_name:
                        session.customer_name = customer_name
                    update_session(session)
                    
                    message = f"🍽️ *{restaurant.name}*\n\n"
                    message += "🔗 *Tap to view menu and order:*\n"
                    message += f"{menu_link}\n\n"
                    message += "✨ Browse menu, add items to cart, and place your order!"
                    
                    response.message(message)
                    return Response(content=str(response), media_type="application/xml")
                else:
                    # Restaurant closed or not found - should not happen, but handle gracefully
                    response.message("❌ This restaurant is currently unavailable. Please try another restaurant.")
                    session.restaurant_id = None
                    session.current_step = "location_request"
                    update_session(session)
                    return Response(content=str(response), media_type="application/xml")
            
            # Regular flow - show restaurant list
            # Find nearby restaurants sorted by distance
            nearby_restaurants = find_restaurants_by_location(latitude, longitude, radius_km=50.0)
            
            if not nearby_restaurants:
                response.message(
                    "😔 Sorry, we couldn't find any restaurants near your location.\n\n"
                    "Please share your location again or try a different area."
                )
                return Response(content=str(response), media_type="application/xml")
            
            # Generate restaurant selection page link with customer name
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
            customer_name_param = urllib.parse.quote(session.customer_name or customer_name or "Customer", safe='')
            restaurants_link = f"{frontend_url}/restaurants?lat={latitude}&lon={longitude}&token={urllib.parse.quote(phone_number, safe='')}&name={customer_name_param}"
            
            # Prepare restaurant list message with clickable link
            message = "📍 *Restaurants Near You*\n\n"
            message += "🔗 *Tap to browse restaurants with filters:*\n"
            message += f"{restaurants_link}\n\n"
            message += "✨ Filter by distance, cuisine type (Veg/Non-Veg/Snack/Full Meal) and select your restaurant!"
            
            # Store restaurant list for text-based selection (fallback)
            restaurant_list = []
            for idx, item in enumerate(nearby_restaurants, 1):
                restaurant = item['restaurant']
                restaurant_list.append({
                    'serial': idx,
                    'id': restaurant.id,
                    'name': restaurant.name.lower()
                })
            
            # Update session with location and restaurant list
            # Save timestamp for location caching (30 minutes validity)
            location_timestamp = datetime.now().isoformat()
            
            if not session:
                session = CustomerSession(
                    phone_number=phone_number,
                    customer_name=customer_name,
                    current_step="restaurant_selection",
                    latitude=latitude,
                    longitude=longitude,
                    location_timestamp=location_timestamp,
                    nearby_restaurants=restaurant_list
                )
                create_session(session)
            else:
                session.current_step = "restaurant_selection"
                session.latitude = latitude
                session.longitude = longitude
                session.location_timestamp = location_timestamp
                session.nearby_restaurants = restaurant_list
                # Update customer name if not set
                if not session.customer_name:
                    session.customer_name = customer_name
                update_session(session)
            
            response.message(message)
            return Response(content=str(response), media_type="application/xml")
            
        except ValueError as e:
            logger.error(f"❌ Invalid location data: {e}")
            response.message("❌ Invalid location. Please share your location again.")
            return Response(content=str(response), media_type="application/xml")
    
    # Handle text messages
    if Body:
        body_text = Body.strip().lower()
        body_original = Body.strip()  # Keep original for restaurant ID extraction
        logger.info(f"💬 Message from {phone_number}: {body_text}")
        
        # Check if this is a QR code scan
        restaurant_id_from_qr = None
        import re
        
        # Method 1: Check if message contains "resto_" pattern (backward compatibility)
        match = re.search(r'resto_([a-zA-Z0-9_]+)', body_original, re.IGNORECASE)
        if match:
            restaurant_id_from_qr = match.group(1)
        
        # Method 2: Check if message is just "Hi/Hello/Hey" and there's a recent QR scan
        # This handles the case where QR code sends just "Hi"
        if not restaurant_id_from_qr and body_text.strip() in ["hi", "hello", "hey"]:
            global _most_recent_qr_scan
            current_time = time.time()
            
            # Check if there's a recent QR scan (within last 3 minutes)
            if _most_recent_qr_scan and (current_time - _most_recent_qr_scan["timestamp"]) < 180:
                restaurant_id_from_qr = _most_recent_qr_scan["restaurant_id"]
                logger.info(f"📱 Matched QR scan to message - Restaurant ID: {restaurant_id_from_qr}")
                # Clear the QR scan after using it (one-time use)
                _most_recent_qr_scan = None
            elif session and session.restaurant_id:
                # Fallback: Use restaurant_id from existing session if available
                restaurant_id_from_qr = session.restaurant_id
        
        if restaurant_id_from_qr:
            logger.info(f"📱 QR code scanned - Restaurant ID: {restaurant_id_from_qr}")
            
            # Get restaurant
            restaurant = get_restaurant_by_id(restaurant_id_from_qr)
            if not restaurant:
                response.message("❌ Restaurant not found. Please scan the QR code again.")
                return Response(content=str(response), media_type="application/xml")
            
            # Check if restaurant is closed
            if not restaurant.is_active:
                # Restaurant is closed - ask if they want to explore other restaurants
                session = get_session_by_phone(phone_number)
                if not session:
                    session = CustomerSession(
                        phone_number=phone_number,
                        customer_name=customer_name,
                        current_step="restaurant_closed_confirm"
                    )
                    create_session(session)
                else:
                    session.current_step = "restaurant_closed_confirm"
                    session.restaurant_id = restaurant_id_from_qr  # Store closed restaurant ID
                    if customer_name and customer_name != "Customer":
                        session.customer_name = customer_name
                    update_session(session)
                
                message = f"🔴 *{restaurant.name} is currently CLOSED*\n\n"
                message += "Would you like to explore other restaurants nearby?\n\n"
                message += "1️⃣ *Yes - Show nearby restaurants*\n"
                message += "2️⃣ *No - Maybe later*"
                
                response.message(message)
                return Response(content=str(response), media_type="application/xml")
            
            # Restaurant is open - check if customer has location
            session = get_session_by_phone(phone_number)
            has_recent_location = False
            if session and session.latitude and session.longitude and session.location_timestamp:
                try:
                    location_time = datetime.fromisoformat(session.location_timestamp)
                    time_diff = datetime.now() - location_time
                    if time_diff <= timedelta(minutes=30):
                        has_recent_location = True
                except (ValueError, TypeError):
                    pass
            
            # Store restaurant ID in session (from QR code)
            if not session:
                session = CustomerSession(
                    phone_number=phone_number,
                    customer_name=customer_name,
                    restaurant_id=restaurant_id_from_qr,
                    current_step="qr_restaurant_selected"
                )
                create_session(session)
            else:
                session.restaurant_id = restaurant_id_from_qr
                session.current_step = "qr_restaurant_selected"
                if customer_name and customer_name != "Customer":
                    session.customer_name = customer_name
                update_session(session)
            
            if has_recent_location:
                # Ask if they want to use same location or change
                session.current_step = "qr_location_confirm"
                update_session(session)
                
                name = session.customer_name or customer_name or "Customer"
                message = f"👋 *Welcome to {restaurant.name}!*\n\n"
                message += f"📍 I have your location from before.\n\n"
                message += "Would you like to:\n\n"
                message += "1️⃣ *Use same location*\n"
                message += "2️⃣ *Change location*"
                
                response.message(message)
                return Response(content=str(response), media_type="application/xml")
            else:
                # No location - ask for location
                session.current_step = "qr_location_request"
                update_session(session)
                
                message = f"👋 *Welcome to {restaurant.name}!*\n\n"
                message += "📍 To continue, please *share your location*.\n\n"
                message += "📱 *How to share location:*\n"
                message += "1. Tap the 📎 (attachment) icon\n"
                message += "2. Select *Location*\n"
                message += "3. Choose *Share Live Location* or *Send Current Location*"
                
                response.message(message)
                return Response(content=str(response), media_type="application/xml")
        
        # Handle restaurant closed confirmation (yes/no)
        if session and session.current_step == "restaurant_closed_confirm":
            if body_text in ["1", "yes", "y", "show restaurants", "nearby"]:
                # Customer wants to explore nearby restaurants - need location
                has_recent_location = False
                if session.latitude and session.longitude and session.location_timestamp:
                    try:
                        location_time = datetime.fromisoformat(session.location_timestamp)
                        time_diff = datetime.now() - location_time
                        if time_diff <= timedelta(minutes=30):
                            has_recent_location = True
                    except (ValueError, TypeError):
                        pass
                
                if has_recent_location:
                    # Use existing location
                    nearby_restaurants = find_restaurants_by_location(session.latitude, session.longitude, radius_km=50.0)
                    
                    if not nearby_restaurants:
                        response.message(
                            "😔 Sorry, we couldn't find any open restaurants near your location.\n\n"
                            "Please try again later."
                        )
                        session.current_step = "none"
                        update_session(session)
                        return Response(content=str(response), media_type="application/xml")
                    
                    # Generate restaurant selection page link
                    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
                    customer_name_param = urllib.parse.quote(session.customer_name or customer_name or "Customer", safe='')
                    restaurants_link = f"{frontend_url}/restaurants?lat={session.latitude}&lon={session.longitude}&token={urllib.parse.quote(phone_number, safe='')}&name={customer_name_param}"
                    
                    message = "📍 *Other Restaurants Near You*\n\n"
                    message += "🔗 *Tap to browse restaurants with filters:*\n"
                    message += f"{restaurants_link}\n\n"
                    message += "✨ Filter by distance, cuisine type (Veg/Non-Veg/Snack/Full Meal) and select your restaurant!"
                    
                    session.current_step = "restaurant_selection"
                    session.restaurant_id = None  # Clear closed restaurant ID
                    update_session(session)
                    
                    response.message(message)
                    return Response(content=str(response), media_type="application/xml")
                else:
                    # Need location
                    session.current_step = "location_request"
                    update_session(session)
                    
                    response.message(
                        "📍 To find restaurants near you, please *share your location*.\n\n"
                        "📱 *How to share location:*\n"
                        "1. Tap the 📎 (attachment) icon\n"
                        "2. Select *Location*\n"
                        "3. Choose *Share Live Location* or *Send Current Location*"
                    )
                    return Response(content=str(response), media_type="application/xml")
            else:
                # Customer chose "No"
                response.message("👍 No problem! Feel free to come back when we're open. 🙏")
                session.current_step = "none"
                update_session(session)
                return Response(content=str(response), media_type="application/xml")
        
        # Handle QR location confirmation (for QR code flow)
        if session and session.current_step == "qr_location_confirm" and session.restaurant_id:
            if body_text in ["1", "same", "yes", "use same", "same location"]:
                # Use same location - redirect to menu
                if session.latitude and session.longitude:
                    restaurant = get_restaurant_by_id(session.restaurant_id)
                    if restaurant and restaurant.is_active:
                        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
                        customer_name_param = urllib.parse.quote(session.customer_name or customer_name or "Customer", safe='')
                        menu_link = f"{frontend_url}/menu/{session.restaurant_id}?token={urllib.parse.quote(phone_number, safe='')}&lat={session.latitude}&lon={session.longitude}&name={customer_name_param}"
                        
                        message = f"🍽️ *{restaurant.name}*\n\n"
                        message += "🔗 *Tap to view menu and order:*\n"
                        message += f"{menu_link}\n\n"
                        message += "✨ Browse menu, add items to cart, and place your order!"
                        
                        session.current_step = "menu"
                        update_session(session)
                        
                        response.message(message)
                        return Response(content=str(response), media_type="application/xml")
            elif body_text in ["2", "change", "no", "new location"]:
                # Change location
                session.current_step = "qr_location_request"
                update_session(session)
                
                response.message(
                    "📍 Please *share your location* to continue.\n\n"
                    "📱 *How to share location:*\n"
                    "1. Tap the 📎 (attachment) icon\n"
                    "2. Select *Location*\n"
                    "3. Choose *Share Live Location* or *Send Current Location*"
                )
                return Response(content=str(response), media_type="application/xml")
        
        # Handle QR location sharing (after QR code scan)
        if session and (session.current_step == "qr_location_request") and session.restaurant_id:
            # This will be handled by the location sharing handler above, but we need to ensure it redirects to menu
            pass  # Will be handled below in location handler
        
        # Check if user wants to restart/start fresh (greetings or restart commands)
        restart_keywords = ["hi", "hello", "hey", "start", "begin", "new", "restart", "menu"]
        if body_text in restart_keywords or (body_text.startswith("hi") or body_text.startswith("hello")):
            # Check if user has a recent location (within 30 minutes)
            has_recent_location = False
            if session and session.latitude and session.longitude and session.location_timestamp:
                try:
                    location_time = datetime.fromisoformat(session.location_timestamp)
                    time_diff = datetime.now() - location_time
                    if time_diff <= timedelta(minutes=30):
                        has_recent_location = True
                except (ValueError, TypeError):
                    pass
            
            if has_recent_location:
                # Ask if they want to use same location or change it
                session.current_step = "location_confirm"
                session.restaurant_id = None
                # Update customer name if provided
                if customer_name and customer_name != "Customer":
                    session.customer_name = customer_name
                update_session(session)
                
                # Create concise message with options
                name = session.customer_name or "Customer"
                message = f"👋 *Welcome back {name}!*\n\n"
                message += "📍 I have your location from before.\n\n"
                message += "Would you like to:\n\n"
                message += "1️⃣ *Use same location*\n"
                message += "2️⃣ *Change location*"
                
                response.message(message)
                return Response(content=str(response), media_type="application/xml")
            else:
                # No recent location, ask for new location
                if session:
                    session.current_step = "location_request"
                    session.restaurant_id = None
                    session.nearby_restaurants = None
                    session.latitude = None
                    session.longitude = None
                    session.location_timestamp = None
                    # Update customer name if provided
                    if customer_name and customer_name != "Customer":
                        session.customer_name = customer_name
                    update_session(session)
                else:
                    session = CustomerSession(
                        phone_number=phone_number,
                        customer_name=customer_name,
                        current_step="location_request"
                    )
                    create_session(session)
                
                response.message(
                    "👋 *Welcome to Food Delivery!*\n\n"
                    "📍 To find restaurants near you, please *share your location*.\n\n"
                    "📱 *How to share location:*\n"
                    "1. Tap the 📎 (attachment) icon\n"
                    "2. Select *Location*\n"
                    "3. Choose *Share Live Location* or *Send Current Location*"
                )
                return Response(content=str(response), media_type="application/xml")
        
        # Handle location confirmation (same or change)
        if session and session.current_step == "location_confirm":
            if body_text in ["1", "same", "yes", "use same", "same location"]:
                # Use same location - fetch restaurants again to ensure fresh data
                if session.latitude and session.longitude:
                    # Find nearby restaurants with saved location
                    nearby_restaurants = find_restaurants_by_location(session.latitude, session.longitude, radius_km=50.0)
                    
                    if not nearby_restaurants:
                        response.message(
                            "😔 Sorry, we couldn't find any restaurants near your saved location.\n\n"
                            "Please share a new location."
                        )
                        session.current_step = "location_request"
                        update_session(session)
                        return Response(content=str(response), media_type="application/xml")
                    
                    # Generate restaurant selection page link with customer name
                    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
                    customer_name_param = urllib.parse.quote(session.customer_name or customer_name or "Customer", safe='')
                    restaurants_link = f"{frontend_url}/restaurants?lat={session.latitude}&lon={session.longitude}&token={urllib.parse.quote(phone_number, safe='')}&name={customer_name_param}"
                    
                    # Prepare restaurant list message with clickable link
                    message = "📍 *Using your previous location*\n\n"
                    message += "🔗 *Tap to browse restaurants with filters:*\n"
                    message += f"{restaurants_link}\n\n"
                    message += "✨ Filter by distance, cuisine type (Veg/Non-Veg/Snack/Full Meal) and select your restaurant!"
                    
                    # Store restaurant list for text-based selection (fallback)
                    restaurant_list = []
                    for idx, item in enumerate(nearby_restaurants, 1):
                        restaurant = item['restaurant']
                        restaurant_list.append({
                            'serial': idx,
                            'id': restaurant.id,
                            'name': restaurant.name.lower()
                        })
                    
                    # Update session with fresh restaurant list
                    session.current_step = "restaurant_selection"
                    session.nearby_restaurants = restaurant_list
                    # Update timestamp to extend validity
                    session.location_timestamp = datetime.now().isoformat()
                    update_session(session)
                    
                    response.message(message)
                    return Response(content=str(response), media_type="application/xml")
                else:
                    # Location data missing, ask for new location
                    session.current_step = "location_request"
                    update_session(session)
                    response.message(
                        "📍 Please share your location again.\n\n"
                        "📱 Tap 📎 → Location → Share Current Location"
                    )
                    return Response(content=str(response), media_type="application/xml")
            
            elif body_text in ["2", "change", "new", "different", "change location"]:
                # User wants to change location
                session.current_step = "location_request"
                session.latitude = None
                session.longitude = None
                session.location_timestamp = None
                session.nearby_restaurants = None
                update_session(session)
                
                response.message(
                    "📍 *Please share your new location.*\n\n"
                    "📱 *How to share location:*\n"
                    "1. Tap the 📎 (attachment) icon\n"
                    "2. Select *Location*\n"
                    "3. Choose *Share Live Location* or *Send Current Location*"
                )
                return Response(content=str(response), media_type="application/xml")
        
        # Check if this is first interaction (no session or location not shared)
        if not session or session.current_step == "location_request":
            # Ask for location
            response.message(
                "👋 *Welcome to Food Delivery!*\n\n"
                "📍 To find restaurants near you, please *share your location*.\n\n"
                "📱 *How to share location:*\n"
                "1. Tap the 📎 (attachment) icon\n"
                "2. Select *Location*\n"
                "3. Choose *Share Live Location* or *Send Current Location*"
            )
            
            # Create session if doesn't exist
            if not session:
                session = CustomerSession(
                    phone_number=phone_number,
                    current_step="location_request"
                )
                create_session(session)
            else:
                session.current_step = "location_request"
                update_session(session)
            
            return Response(content=str(response), media_type="application/xml")
        
        # Handle restaurant selection
        if session.current_step == "restaurant_selection":
            if not session.nearby_restaurants:
                # Session is in restaurant_selection but no restaurants stored
                # Reset to location request
                response.message(
                    "📍 Please share your location again to see nearby restaurants."
                )
                session.current_step = "location_request"
                update_session(session)
                return Response(content=str(response), media_type="application/xml")
            
            selected_restaurant = None
            
            # Try to match by serial number
            try:
                serial_num = int(body_text)
                for item in session.nearby_restaurants:
                    if item['serial'] == serial_num:
                        selected_restaurant = get_restaurant_by_id(item['id'])
                        break
            except ValueError:
                # Not a number, try matching by name (body_text is already lowercased)
                for item in session.nearby_restaurants:
                    # Compare lowercase names
                    if item['name'] == body_text or body_text in item['name']:
                        selected_restaurant = get_restaurant_by_id(item['id'])
                        break
            
            if not selected_restaurant:
                response.message(
                    "❌ Restaurant not found. Please reply with a valid restaurant number or name from the list above."
                )
                return Response(content=str(response), media_type="application/xml")
            
            # Fetch menu items for selected restaurant
            menu_items = get_products_by_restaurant(selected_restaurant.id)
            
            if not menu_items:
                response.message(
                    f"😔 Sorry, *{selected_restaurant.name}* doesn't have a menu available at the moment.\n\n"
                    "Please try selecting another restaurant."
                )
                return Response(content=str(response), media_type="application/xml")
            
            # Update session with selected restaurant
            session.restaurant_id = selected_restaurant.id
            session.current_step = "menu"
            update_session(session)
            
            # Generate menu link pointing to FRONTEND (not backend)
            # Frontend will handle the UI and call backend API
            frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")  # Frontend URL (Next.js)
            # URL encode the phone number token properly
            menu_link = f"{frontend_url}/menu/{selected_restaurant.id}?token={urllib.parse.quote(phone_number, safe='')}"
            
            # Create message with interactive button for better UX
            # WhatsApp automatically detects URLs and makes them clickable
            # Format: Put URL on its own line for best clickability
            menu_message = f"✅ *{selected_restaurant.name}* selected!\n\n"
            menu_message += "🍽️ *View Menu & Place Order*\n"
            menu_message += "━━━━━━━━━━━━━━━━\n\n"
            menu_message += "📱 *Tap the link below to view menu:*\n\n"
            
            # Put URL on its own line - WhatsApp will auto-detect and make it clickable
            # The URL will be shown but will be clickable
            menu_message += f"{menu_link}\n\n"
            
            menu_message += "✨ Add items to cart and place order securely.\n\n"
            menu_message += "🙏 Thank you for choosing us!"
            
            # Send message - WhatsApp will automatically make the URL clickable
            # Note: WhatsApp shows the URL but makes it blue and clickable
            # To hide URL completely, you need WhatsApp Button Messages (requires template approval)
            response.message(menu_message)
            return Response(content=str(response), media_type="application/xml")
        
        # Handle menu/ordering (if restaurant is already selected)
        if session.current_step == "menu" and session.restaurant_id:
            # For now, just acknowledge the order request
            # TODO: Implement full order processing
            response.message(
                "✅ Order received! We're processing your order.\n\n"
                "Your order details will be confirmed shortly."
            )
            return Response(content=str(response), media_type="application/xml")
        
        # Default response - check if this is first time
        if session and session.latitude and session.longitude and session.location_timestamp:
            # Has location, ask if they want to use it
            try:
                location_time = datetime.fromisoformat(session.location_timestamp)
                time_diff = datetime.now() - location_time
                if time_diff <= timedelta(minutes=30):
                    # Recent location exists, ask to use it
                    session.current_step = "location_confirm"
                    if customer_name and customer_name != "Customer":
                        session.customer_name = customer_name
                    update_session(session)
                    
                    name = session.customer_name or customer_name or "Customer"
                    response.message(
                        f"👋 *Welcome back {name}!*\n\n"
                        "📍 Would you like to use the same location you shared earlier?\n\n"
                        "1️⃣ *Use same location*\n"
                        "2️⃣ *Change location*"
                    )
                    return Response(content=str(response), media_type="application/xml")
            except (ValueError, TypeError):
                pass
        
        # First time or no recent location - ask for location
        if session:
            session.current_step = "location_request"
            if customer_name and customer_name != "Customer":
                session.customer_name = customer_name
            update_session(session)
        else:
            session = CustomerSession(
                phone_number=phone_number,
                customer_name=customer_name,
                current_step="location_request"
            )
            create_session(session)
        
    response.message(
            "👋 *Welcome to Food Delivery!*\n\n"
            "📍 To find restaurants near you, please *share your location*.\n\n"
            "📱 *How to share location:*\n"
            "1. Tap the 📎 (attachment) icon\n"
            "2. Select *Location*\n"
            "3. Choose *Share Live Location* or *Send Current Location*"
        )
    return Response(content=str(response), media_type="application/xml")

# -------------------------------
# Menu Webpage Endpoint
# -------------------------------
# Public API endpoint to get filtered restaurants (for restaurant selection page)
@app.get("/api/public/restaurants")
async def get_filtered_restaurants(
    latitude: float = Query(...),
    longitude: float = Query(...),
    max_distance: float = Query(50.0, description="Maximum distance in km"),
    cuisine_type: Optional[str] = Query(None, description="Filter by cuisine: veg, non-veg, both, snack, full-meal")
):
    """Public endpoint to get restaurants filtered by location, distance, and cuisine type"""
    logger.info(f"📋 Fetching restaurants - lat={latitude}, lon={longitude}, max_dist={max_distance}, cuisine={cuisine_type}")
    
    # Find nearby restaurants
    nearby_restaurants = find_restaurants_by_location(latitude, longitude, radius_km=max_distance)
    
    # Filter by cuisine type if specified
    if cuisine_type and cuisine_type.lower() != "all":
        filtered_restaurants = []
        filter_cuisine = cuisine_type.lower()
        
        for item in nearby_restaurants:
            restaurant = item['restaurant']
            # Get restaurant cuisine type (default to "both" if not set)
            restaurant_cuisine = getattr(restaurant, 'cuisine_type', 'both').lower()
            
            # Match logic
            should_include = False
            
            if filter_cuisine == "veg":
                # Veg filter: show restaurants that serve veg (veg, both, full-meal)
                should_include = restaurant_cuisine in ["veg", "both", "full-meal"]
            elif filter_cuisine == "non-veg":
                # Non-veg filter: show restaurants that serve non-veg (non-veg, both, full-meal)
                should_include = restaurant_cuisine in ["non-veg", "both", "full-meal"]
            elif filter_cuisine == "snack":
                # Snack filter: show only snack restaurants
                should_include = restaurant_cuisine == "snack"
            elif filter_cuisine == "full-meal":
                # Full meal filter: show full-meal restaurants
                should_include = restaurant_cuisine == "full-meal"
            elif filter_cuisine == "both":
                # Both filter: show restaurants that serve both
                should_include = restaurant_cuisine in ["both", "full-meal"]
            else:
                # Exact match for any other cuisine type
                should_include = restaurant_cuisine == filter_cuisine
            
            if should_include:
                filtered_restaurants.append(item)
        
        nearby_restaurants = filtered_restaurants
    
    # Format response with ratings
    restaurants_list = []
    for idx, item in enumerate(nearby_restaurants, 1):
        restaurant = item['restaurant']
        # Get rating information from the item (already calculated in find_restaurants_by_location)
        rating_info = {
            'rating': item.get('rating', 4.0),  # Overall rating (1-5)
            'customer_rating': item.get('customer_rating'),  # Average customer rating
            'total_orders': item.get('total_orders', 0)  # Total orders count
        }
        
        # Check if restaurant has any discounted items
        menu_items = get_products_by_restaurant(restaurant.id)
        has_discount = any(item.discounted_price and item.discounted_price < item.price for item in menu_items)
        max_discount_percentage = 0
        if has_discount:
            for item in menu_items:
                if item.discounted_price and item.discounted_price < item.price:
                    discount_pct = ((item.price - item.discounted_price) / item.price) * 100
                    max_discount_percentage = max(max_discount_percentage, round(discount_pct, 1))
        
        restaurants_list.append({
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "distance": round(item['distance'], 1),
            "delivery_fee": restaurant.delivery_fee,
            "cuisine_type": getattr(restaurant, 'cuisine_type', 'both'),
            "serial": idx,
            "rating": rating_info['rating'],
            "customer_rating": rating_info['customer_rating'],
            "total_orders": rating_info['total_orders'],
            "has_discount": has_discount,
            "max_discount_percentage": max_discount_percentage if has_discount else None
        })
    
    return {
        "restaurants": restaurants_list,
        "total": len(restaurants_list),
        "filters": {
            "latitude": latitude,
            "longitude": longitude,
            "max_distance": max_distance,
            "cuisine_type": cuisine_type or "all"
        }
    }

# Public API endpoint for frontend to fetch menu (no auth required)
@app.get("/api/public/menu/{restaurant_id}")
async def get_public_menu(restaurant_id: str):
    """Public endpoint to get restaurant menu for customers (no authentication required)
    This endpoint is fully dynamic - returns menu for any restaurant_id provided in the URL
    """
    logger.info(f"📋 Fetching menu for restaurant: {restaurant_id}")
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        logger.warning(f"❌ Restaurant not found: {restaurant_id}")
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    menu_items = get_products_by_restaurant(restaurant_id)
    
    # Group items by category - include all items (available and unavailable)
    categories = {}
    for item in menu_items:
        category = item.category or "Other"
        if category not in categories:
            categories[category] = []
        # Calculate discount percentage
        discount_percentage = None
        if item.discounted_price and item.discounted_price < item.price:
            discount_percentage = round(((item.price - item.discounted_price) / item.price) * 100, 1)
        
        categories[category].append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "price": item.price,
            "discounted_price": item.discounted_price,
            "discount_percentage": discount_percentage,
            "is_available": item.is_available
        })
    
    # Sort items within each category: available first, then unavailable
    for category in categories:
        categories[category].sort(key=lambda x: (not x["is_available"], x["name"]))
    
    # Convert to list format
    category_list = [
        {
            "name": category,
            "items": items
        }
        for category, items in categories.items()
    ]
    
    return {
        "restaurant": {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "delivery_fee": restaurant.delivery_fee,
            "upi_id": restaurant.upi_id
        },
        "categories": category_list
    }

# Temporary storage for QR code scans (stores most recent restaurant_id)
# Since we can't reliably match QR scan to phone number until message arrives,
# we'll store the most recent restaurant_id and use it if "Hi" arrives within a short window
_most_recent_qr_scan = None

# -----------------------------------
# Browser Simulation Endpoint (for testing)
# -----------------------------------
@app.get("/simulate", response_class=HTMLResponse)
def simulate():
    """Browser UI to simulate WhatsApp messages for testing"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsApp Message Simulator</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            h1 {
                color: #25D366;
                margin-bottom: 10px;
            }
            .subtitle {
                color: #666;
                margin-bottom: 30px;
            }
            form {
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #333;
            }
            input, textarea, select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                font-size: 14px;
                box-sizing: border-box;
            }
            textarea {
                min-height: 100px;
                resize: vertical;
            }
            button {
                background: #25D366;
                color: white;
                padding: 12px 30px;
                border: none;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                margin-right: 10px;
            }
            button:hover {
                background: #20BA5A;
            }
            .quick-actions {
                margin-top: 20px;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }
            .quick-btn {
                background: #667eea;
                padding: 8px 15px;
                font-size: 14px;
                margin: 5px;
            }
            .response {
                margin-top: 30px;
                padding: 20px;
                background: #e8f5e9;
                border-left: 4px solid #4caf50;
                border-radius: 5px;
                white-space: pre-wrap;
                font-family: monospace;
            }
            .error {
                background: #ffebee;
                border-left-color: #f44336;
            }
            .preset {
                display: inline-block;
                margin: 5px;
                padding: 8px 12px;
                background: #f0f0f0;
                border: 1px solid #ddd;
                border-radius: 5px;
                cursor: pointer;
                font-size: 13px;
            }
            .preset:hover {
                background: #e0e0e0;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>📱 WhatsApp Message Simulator</h1>
            <p class="subtitle">Test your WhatsApp webhook without actually sending WhatsApp messages</p>
            
            <form id="simulateForm" action="/whatsapp" method="post">
                <div class="form-group">
                    <label for="From">From (Phone Number):</label>
                    <input type="text" id="From" name="From" value="whatsapp:+919452151637" required>
                    <small style="color: #666;">Format: whatsapp:+91XXXXXXXXXX</small>
                </div>
                
                <div class="form-group">
                    <label for="Body">Message Body:</label>
                    <textarea id="Body" name="Body" required>Hi</textarea>
                    <div style="margin-top: 10px;">
                        <strong>Quick Presets:</strong><br>
                        <span class="preset" onclick="setMessage('Hi')">Hi</span>
                        <span class="preset" onclick="setMessage('Hello')">Hello</span>
                        <span class="preset" onclick="setMessage('1')">Select Restaurant 1</span>
                        <span class="preset" onclick="setMessage('2')">Select Restaurant 2</span>
                        <span class="preset" onclick="setLocation()">Share Location</span>
                        <span class="preset" onclick="setMessage('resto_rest_005')">QR Code Scan</span>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="Latitude">Latitude (optional):</label>
                    <input type="text" id="Latitude" name="Latitude" placeholder="26.7756833">
                </div>
                
                <div class="form-group">
                    <label for="Longitude">Longitude (optional):</label>
                    <input type="text" id="Longitude" name="Longitude" placeholder="80.91468">
                </div>
                
                <div class="form-group">
                    <label for="ProfileName">Profile Name (optional):</label>
                    <input type="text" id="ProfileName" name="ProfileName" placeholder="John Doe">
                </div>
                
                <button type="submit">📤 Send Message</button>
            </form>
            
            <div id="response" style="display:none;"></div>
        </div>
        
        <script>
            function setMessage(text) {
                document.getElementById('Body').value = text;
            }
            
            function setLocation() {
                document.getElementById('Latitude').value = '26.7756833';
                document.getElementById('Longitude').value = '80.91468';
                setMessage('Location shared');
            }
            
            document.getElementById('simulateForm').addEventListener('submit', async function(e) {
                e.preventDefault();
                
                const formData = new FormData(this);
                const responseDiv = document.getElementById('response');
                responseDiv.style.display = 'block';
                responseDiv.className = 'response';
                responseDiv.textContent = 'Sending...';
                
                try {
                    const response = await fetch('/whatsapp', {
                        method: 'POST',
                        body: formData
                    });
                    
                    let result;
                    if (response.headers.get('content-type')?.includes('application/xml')) {
                        // Parse XML response
                        const text = await response.text();
                        const parser = new DOMParser();
                        const xml = parser.parseFromString(text, 'text/xml');
                        const message = xml.querySelector('Message');
                        result = message ? message.textContent : text;
                    } else {
                        result = await response.text();
                    }
                    
                    responseDiv.textContent = result;
                    responseDiv.className = response.ok ? 'response' : 'response error';
                } catch (error) {
                    responseDiv.className = 'response error';
                    responseDiv.textContent = 'Error: ' + error.message;
                }
            });
        </script>
    </body>
    </html>
    """

# QR Code Redirect Endpoint - Stores restaurant ID and redirects to WhatsApp with just "Hi"
@app.get("/qr/{restaurant_id}")
async def qr_redirect(restaurant_id: str, request: Request):
    """
    Redirect endpoint for QR codes.
    Stores restaurant_id temporarily and redirects to WhatsApp with just "Hi".
    Backend will use the most recent QR scan when "Hi" message arrives.
    """
    global _most_recent_qr_scan
    from services.whatsapp_service import TWILIO_WHATSAPP_NUMBER
    from fastapi.responses import RedirectResponse, HTMLResponse
    
    # Validate restaurant exists
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        return HTMLResponse(content=f"<h1>Restaurant not found: {restaurant_id}</h1>", status_code=404)
    
    # Store most recent QR scan (with timestamp)
    _most_recent_qr_scan = {
        "restaurant_id": restaurant_id,
        "timestamp": time.time()
    }
    
    logger.info(f"📱 QR code scanned for restaurant: {restaurant_id}")
    
    # Extract Twilio number
    twilio_number = TWILIO_WHATSAPP_NUMBER.replace("whatsapp:", "").replace("+", "").strip()
    
    # Redirect to WhatsApp with just "Hi"
    whatsapp_url = f"https://wa.me/{twilio_number}?text=Hi"
    return RedirectResponse(url=whatsapp_url, status_code=302)

# Keep old HTML endpoint for backward compatibility (deprecated - use frontend instead)
@app.get("/menu/{restaurant_id}", response_class=HTMLResponse)
async def menu_page_legacy(restaurant_id: str, token: str = Query(...)):
    """Display menu page with order form"""
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    menu_items = get_products_by_restaurant(restaurant_id)
    available_items = [item for item in menu_items if item.is_available]
    
    # Build menu HTML
    menu_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{restaurant.name} - Menu</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                font-size: 28px;
                margin-bottom: 10px;
            }}
            .header p {{
                opacity: 0.9;
                font-size: 14px;
            }}
            .menu-section {{
                padding: 25px;
            }}
            .menu-item {{
                border: 2px solid #f0f0f0;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 15px;
                transition: all 0.3s;
            }}
            .menu-item:hover {{
                border-color: #667eea;
                box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
            }}
            .menu-item h3 {{
                color: #333;
                font-size: 20px;
                margin-bottom: 8px;
            }}
            .menu-item p {{
                color: #666;
                font-size: 14px;
                margin-bottom: 12px;
            }}
            .menu-item .price {{
                color: #667eea;
                font-size: 22px;
                font-weight: bold;
                margin-bottom: 12px;
            }}
            .quantity-control {{
                display: flex;
                align-items: center;
                gap: 15px;
            }}
            .quantity-btn {{
                width: 40px;
                height: 40px;
                border: 2px solid #667eea;
                background: white;
                color: #667eea;
                border-radius: 8px;
                font-size: 20px;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .quantity-btn:hover {{
                background: #667eea;
                color: white;
            }}
            .quantity-input {{
                width: 60px;
                height: 40px;
                border: 2px solid #ddd;
                border-radius: 8px;
                text-align: center;
                font-size: 18px;
            }}
            .order-section {{
                padding: 25px;
                background: #f8f9fa;
                border-top: 2px solid #eee;
            }}
            .form-group {{
                margin-bottom: 20px;
            }}
            .form-group label {{
                display: block;
                margin-bottom: 8px;
                color: #333;
                font-weight: 600;
            }}
            .form-group input, .form-group select, .form-group textarea {{
                width: 100%;
                padding: 12px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                font-family: inherit;
            }}
            .form-group textarea {{
                resize: vertical;
                min-height: 80px;
            }}
            .payment-options {{
                display: flex;
                gap: 15px;
                margin-top: 10px;
            }}
            .payment-option {{
                flex: 1;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 8px;
                text-align: center;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .payment-option input[type="radio"] {{
                display: none;
            }}
            .payment-option.active {{
                border-color: #667eea;
                background: #f0f4ff;
            }}
            .total-section {{
                background: white;
                padding: 20px;
                border-radius: 12px;
                margin-bottom: 20px;
            }}
            .total-row {{
                display: flex;
                justify-content: space-between;
                margin-bottom: 10px;
                font-size: 16px;
            }}
            .total-row.total {{
                font-size: 24px;
                font-weight: bold;
                color: #667eea;
                border-top: 2px solid #eee;
                padding-top: 10px;
                margin-top: 10px;
            }}
            .submit-btn {{
                width: 100%;
                padding: 18px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 12px;
                font-size: 18px;
                font-weight: bold;
                cursor: pointer;
                transition: all 0.3s;
            }}
            .submit-btn:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
            }}
            .submit-btn:disabled {{
                opacity: 0.6;
                cursor: not-allowed;
            }}
            .hidden {{
                display: none;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🍽️ {restaurant.name}</h1>
                <p>Select items and place your order</p>
            </div>
            
            <form id="orderForm" method="POST" action="/submit-order">
                <input type="hidden" name="restaurant_id" value="{restaurant_id}">
                <input type="hidden" name="token" value="{token}">
                
                <div class="menu-section">
    """
    
    for item in available_items:
        menu_html += f"""
                    <div class="menu-item">
                        <h3>{item.name}</h3>
                        <p>{item.description}</p>
                        <div class="price">₹{item.price:.0f}</div>
                        <div class="quantity-control">
                            <button type="button" class="quantity-btn" onclick="decreaseQty('{item.id}')">-</button>
                            <input type="number" 
                                   id="qty_{item.id}" 
                                   name="items[{item.id}]" 
                                   value="0" 
                                   min="0" 
                                   class="quantity-input"
                                   data-price="{item.price}"
                                   data-product-id="{item.id}"
                                   data-product-name="{item.name}"
                                   onchange="updateTotal()">
                            <button type="button" class="quantity-btn" onclick="increaseQty('{item.id}')">+</button>
                        </div>
                    </div>
        """
    
    menu_html += f"""
                </div>
                
                <div class="order-section">
                    <div class="form-group">
                        <label for="customer_name">Your Name *</label>
                        <input type="text" id="customer_name" name="customer_name" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="order_type">Order Type *</label>
                        <select id="order_type" name="order_type" required onchange="toggleAddress()">
                            <option value="pickup">Pickup</option>
                            <option value="delivery">Delivery</option>
                        </select>
                    </div>
                    
                    <div class="form-group" id="addressGroup" style="display:none;">
                        <label for="delivery_address">Delivery Address *</label>
                        <textarea id="delivery_address" name="delivery_address" placeholder="Enter your delivery address"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label>Payment Method *</label>
                        <div class="payment-options">
                            <label class="payment-option" onclick="selectPayment('cod')">
                                <input type="radio" name="payment_method" value="cod" required>
                                💵 Cash on Delivery
                            </label>
                            <label class="payment-option" onclick="selectPayment('online')">
                                <input type="radio" name="payment_method" value="online" required>
                                💳 Online Payment
                            </label>
                        </div>
                    </div>
                    
                    <div class="total-section">
                        <div class="total-row">
                            <span>Subtotal:</span>
                            <span id="subtotal">₹0</span>
                        </div>
                        <div class="total-row">
                            <span>Delivery Fee:</span>
                            <span id="deliveryFee">₹0</span>
                        </div>
                        <div class="total-row total">
                            <span>Total:</span>
                            <span id="total">₹0</span>
                        </div>
                    </div>
                    
                    <button type="submit" class="submit-btn" id="submitBtn" disabled>Place Order</button>
                </div>
            </form>
        </div>
        
        <script>
            const deliveryFee = {restaurant.delivery_fee};
            
            function increaseQty(productId) {{
                const input = document.getElementById('qty_' + productId);
                const current = parseInt(input.value) || 0;
                input.value = current + 1;
                updateTotal();
                checkSubmitButton();
            }}
            
            function decreaseQty(productId) {{
                const input = document.getElementById('qty_' + productId);
                const current = parseInt(input.value) || 0;
                if (current > 0) {{
                    input.value = current - 1;
                    updateTotal();
                    checkSubmitButton();
                }}
            }}
            
            function updateTotal() {{
                let subtotal = 0;
                const inputs = document.querySelectorAll('.quantity-input');
                inputs.forEach(input => {{
                    const qty = parseInt(input.value) || 0;
                    const price = parseFloat(input.dataset.price);
                    subtotal += qty * price;
                }});
                
                const orderType = document.getElementById('order_type').value;
                const fee = orderType === 'delivery' ? deliveryFee : 0;
                const total = subtotal + fee;
                
                document.getElementById('subtotal').textContent = '₹' + subtotal.toFixed(0);
                document.getElementById('deliveryFee').textContent = '₹' + fee.toFixed(0);
                document.getElementById('total').textContent = '₹' + total.toFixed(0);
            }}
            
            function toggleAddress() {{
                const orderType = document.getElementById('order_type').value;
                const addressGroup = document.getElementById('addressGroup');
                if (orderType === 'delivery') {{
                    addressGroup.style.display = 'block';
                    document.getElementById('delivery_address').required = true;
                }} else {{
                    addressGroup.style.display = 'none';
                    document.getElementById('delivery_address').required = false;
                }}
                updateTotal();
            }}
            
            function selectPayment(method) {{
                document.querySelectorAll('.payment-option').forEach(opt => {{
                    opt.classList.remove('active');
                }});
                event.currentTarget.classList.add('active');
                document.querySelector(`input[value="${{method}}"]`).checked = true;
                checkSubmitButton();
            }}
            
            function checkSubmitButton() {{
                const form = document.getElementById('orderForm');
                const submitBtn = document.getElementById('submitBtn');
                const hasItems = Array.from(document.querySelectorAll('.quantity-input')).some(input => parseInt(input.value) > 0);
                
                if (hasItems && form.checkValidity()) {{
                    submitBtn.disabled = false;
                }} else {{
                    submitBtn.disabled = true;
                }}
            }}
            
            // Check on form changes
            document.getElementById('orderForm').addEventListener('change', checkSubmitButton);
            document.getElementById('orderForm').addEventListener('input', checkSubmitButton);
            
            // Initialize
            updateTotal();
        </script>
    </body>
    </html>
    """
    
    return HTMLResponse(content=menu_html)

# -------------------------------
# Order Submission Endpoint
# -------------------------------
@app.post("/submit-order")
async def submit_order(request: Request):
    """Handle order submission from menu page"""
    form_data = await request.form()
    
    restaurant_id = form_data.get("restaurant_id")
    token = form_data.get("token")  # phone_number
    customer_name = form_data.get("customer_name")
    order_type = form_data.get("order_type")
    payment_method = form_data.get("payment_method")
    delivery_address = form_data.get("delivery_address", None)
    
    if not all([restaurant_id, token, customer_name, order_type, payment_method]):
        raise HTTPException(status_code=400, detail="Missing required fields")
    
    if order_type == "delivery" and not delivery_address:
        raise HTTPException(status_code=400, detail="Delivery address required for delivery orders")
    
    # Get restaurant
    restaurant = get_restaurant_by_id(restaurant_id)
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")
    
    # Parse items from form
    items_data = []
    for key, value in form_data.items():
        if key.startswith("items[") and value and int(value) > 0:
            product_id = key.replace("items[", "").replace("]", "")
            quantity = int(value)
            
            # Get product details
            from repositories.product_repo import get_product_by_id
            product = get_product_by_id(product_id)
            if product and product.restaurant_id == restaurant_id:
                items_data.append({
                    "product_id": product_id,
                    "quantity": quantity
                })
    
    if not items_data:
        raise HTTPException(status_code=400, detail="Please select at least one item")
    
    # Get or create customer
    customer_phone = token
    customer = get_customer_by_phone(customer_phone)
    if not customer:
        customer_id = str(uuid.uuid4().int % 1000000)
        customer = create_customer(Customer(
            id=customer_id,
            restaurant_id=restaurant_id,
            phone=customer_phone,
            latitude=0.0,
            longitude=0.0
        ))
    
    # Create order
    try:
        new_order = create_new_order(
            restaurant_id=restaurant_id,
            customer_id=customer.id,
            customer_phone=customer_phone,
            customer_name=customer_name,
            items_data=items_data,
            order_type=order_type,
            delivery_address=delivery_address
        )
        
        # Update order with payment method
        from repositories.order_repo import update_order
        new_order.payment_status = "pending" if payment_method == "cod" else "pending"
        new_order = update_order(new_order)
        
        # Send order confirmation WhatsApp notification
        try:
            await send_order_confirmation(new_order)
        except Exception as e:
            logger.error(f"Failed to send order confirmation: {e}")
        
        # Redirect to payment/confirmation page
        return HTMLResponse(content=f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Order Confirmation</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    padding: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                .container {{
                    max-width: 500px;
                    background: white;
                    border-radius: 20px;
                    padding: 40px;
                    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                    text-align: center;
                }}
                .success-icon {{
                    font-size: 80px;
                    margin-bottom: 20px;
                }}
                h1 {{
                    color: #333;
                    margin-bottom: 20px;
                }}
                .order-details {{
                    text-align: left;
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 12px;
                    margin: 20px 0;
                }}
                .detail-row {{
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 10px;
                    padding-bottom: 10px;
                    border-bottom: 1px solid #eee;
                }}
                .detail-row:last-child {{
                    border-bottom: none;
                    font-weight: bold;
                    font-size: 20px;
                    color: #667eea;
                }}
                .payment-section {{
                    margin-top: 30px;
                    padding: 20px;
                    background: #fff3cd;
                    border-radius: 12px;
                    border: 2px solid #ffc107;
                }}
                .payment-link {{
                    display: inline-block;
                    margin-top: 15px;
                    padding: 15px 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 12px;
                    font-weight: bold;
                }}
                .payment-link:hover {{
                    transform: translateY(-2px);
                    box-shadow: 0 8px 20px rgba(102, 126, 234, 0.4);
                }}
                .info-text {{
                    color: #666;
                    font-size: 14px;
                    margin-top: 20px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <h1>Order Placed Successfully!</h1>
                <p style="color: #666;">Order ID: {new_order.id}</p>
                
                <div class="order-details">
                    <div class="detail-row">
                        <span>Restaurant:</span>
                        <span>{restaurant.name}</span>
                    </div>
                    <div class="detail-row">
                        <span>Order Type:</span>
                        <span>{order_type.title()}</span>
                    </div>
                    <div class="detail-row">
                        <span>Items:</span>
                        <span>{len(new_order.items)}</span>
                    </div>
                    <div class="detail-row">
                        <span>Total Amount:</span>
                        <span>₹{new_order.total_amount:.0f}</span>
                    </div>
                </div>
                
                {"<div class='payment-section'><h3>💳 Payment Required</h3><p>Please complete payment to confirm your order.</p><a href='#' class='payment-link' onclick='window.location.href=`upi://pay?pa=" + restaurant.upi_id + "&pn=" + restaurant.name + "&am=" + str(int(new_order.total_amount)) + "&cu=INR`; return false;'>Pay Now - ₹" + str(int(new_order.total_amount)) + "</a><p class='info-text'>Or send ₹" + str(int(new_order.total_amount)) + " to " + restaurant.upi_id + "</p></div>" if payment_method == "online" and restaurant.upi_id else "<div class='payment-section'><h3>💵 Cash on Delivery</h3><p>Please keep exact change ready for delivery.</p></div>"}
                
                <p class="info-text">
                    You will receive WhatsApp notifications about your order status.<br>
                    Thank you for your order! 🙏
                </p>
            </div>
            
            <script>
                // Send WhatsApp notification about order confirmation
                setTimeout(() => {{
                    // Notification will be sent by the system
                }}, 1000);
            </script>
        </body>
        </html>
        """)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# -------------------------------
# Send Order Confirmation WhatsApp Notification
# -------------------------------
async def send_order_confirmation(order: Order):
    """Send order confirmation via WhatsApp"""
    from services.whatsapp_service import send_order_status_notification
    # Send pending status notification (order confirmation)
    await send_order_status_notification(order, "pending")