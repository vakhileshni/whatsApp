"""
SQLAlchemy Database Models
These models map to the PostgreSQL database tables
"""
from sqlalchemy import Column, String, Integer, Float, Boolean, Text, Date, DateTime, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class RestaurantDB(Base):
    """Restaurant model for database"""
    __tablename__ = 'restaurants'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=False)
    address = Column(Text, nullable=False)
    latitude = Column(DECIMAL(10, 8), nullable=False)
    longitude = Column(DECIMAL(11, 8), nullable=False)
    delivery_fee = Column(DECIMAL(10, 2), nullable=False, default=40.00)
    is_active = Column(Boolean, nullable=False, default=True)
    upi_id = Column(String(255), default='')
    upi_password = Column(String(255), default='')
    upi_qr_code = Column(Text, default='')  # Store QR code as base64 or URL
    cuisine_type = Column(String(50), nullable=False, default='both')
    subscription_plan = Column(String(50), default='free')
    subscription_end_date = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    users = relationship("UserDB", back_populates="restaurant", cascade="all, delete-orphan")
    products = relationship("ProductDB", back_populates="restaurant", cascade="all, delete-orphan")
    orders = relationship("OrderDB", back_populates="restaurant", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'address': self.address,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'delivery_fee': float(self.delivery_fee),
            'is_active': self.is_active,
            'upi_id': self.upi_id,
            'upi_password': self.upi_password,
            'upi_qr_code': self.upi_qr_code,
            'cuisine_type': self.cuisine_type,
            'subscription_plan': self.subscription_plan,
            'subscription_end_date': self.subscription_end_date.isoformat() if self.subscription_end_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class UserDB(Base):
    """User model for database"""
    __tablename__ = 'users'
    
    id = Column(String(50), primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Multi-Factor Authentication (MFA)
    two_factor_enabled = Column(Boolean, nullable=False, default=False)
    two_factor_secret = Column(String(255), nullable=True)  # TOTP secret key
    two_factor_backup_codes = Column(Text, nullable=True)  # JSON array of backup codes
    
    # Relationships
    restaurant = relationship("RestaurantDB", back_populates="users")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'restaurant_id': self.restaurant_id,
            'name': self.name,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_active': self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
        }


class ProductDB(Base):
    """Product model for database"""
    __tablename__ = 'products'
    
    id = Column(String(50), primary_key=True)
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(DECIMAL(10, 2), nullable=False)
    discounted_price = Column(DECIMAL(10, 2), nullable=True)
    discount_percentage = Column(DECIMAL(5, 2), nullable=True)
    category = Column(String(100), nullable=False)
    is_available = Column(Boolean, nullable=False, default=True)
    image_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    restaurant = relationship("RestaurantDB", back_populates="products")
    order_items = relationship("OrderItemDB", back_populates="product")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'discounted_price': float(self.discounted_price) if self.discounted_price else None,
            'discount_percentage': float(self.discount_percentage) if self.discount_percentage else None,
            'category': self.category,
            'is_available': self.is_available,
            'image_url': self.image_url,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class CustomerDB(Base):
    """Customer model for database"""
    __tablename__ = 'customers'
    
    id = Column(String(50), primary_key=True)
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='SET NULL'), nullable=True)
    phone = Column(String(20), unique=True, nullable=False)
    name = Column(String(255), nullable=True)
    latitude = Column(DECIMAL(10, 8), default=0.0)
    longitude = Column(DECIMAL(11, 8), default=0.0)
    last_location_update = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    orders = relationship("OrderDB", back_populates="customer")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'phone': self.phone,
            'name': self.name,
            'latitude': float(self.latitude),
            'longitude': float(self.longitude),
            'last_location_update': self.last_location_update.isoformat() if self.last_location_update else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class OrderDB(Base):
    """Order model for database"""
    __tablename__ = 'orders'
    
    id = Column(String(50), primary_key=True)
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    customer_id = Column(String(50), ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_name = Column(String(255), nullable=False)
    order_type = Column(String(20), nullable=False)  # 'pickup' or 'delivery'
    status = Column(String(20), nullable=False, default='pending')  # Renamed from order_status
    delivery_fee = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    subtotal = Column(DECIMAL(10, 2), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String(20), nullable=False, default='cod')
    payment_status = Column(String(20), nullable=False, default='pending')
    customer_upi_name = Column(String(255), nullable=True)
    delivery_address = Column(Text, nullable=True)
    customer_rating = Column(DECIMAL(3, 2), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    restaurant = relationship("RestaurantDB", back_populates="orders")
    customer = relationship("CustomerDB", back_populates="orders")
    items = relationship("OrderItemDB", back_populates="order", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'customer_id': self.customer_id,
            'customer_phone': self.customer_phone,
            'customer_name': self.customer_name,
            'order_type': self.order_type,
            'status': self.status,
            'delivery_fee': float(self.delivery_fee),
            'subtotal': float(self.subtotal),
            'total_amount': float(self.total_amount),
            'payment_method': self.payment_method,
            'payment_status': self.payment_status,
            'customer_upi_name': self.customer_upi_name,
            'delivery_address': self.delivery_address,
            'customer_rating': float(self.customer_rating) if self.customer_rating else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class OrderItemDB(Base):
    """Order item model for database"""
    __tablename__ = 'order_items'
    
    id = Column(String(50), primary_key=True)
    order_id = Column(String(50), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = Column(String(50), ForeignKey('products.id', ondelete='RESTRICT'), nullable=False)
    product_name = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    order = relationship("OrderDB", back_populates="items")
    product = relationship("ProductDB", back_populates="order_items")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'order_id': self.order_id,
            'product_id': self.product_id,
            'product_name': self.product_name,
            'quantity': self.quantity,
            'price': float(self.price),
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class CustomerSessionDB(Base):
    """Customer session model for database"""
    __tablename__ = 'customer_sessions'
    
    phone_number = Column(String(20), primary_key=True)
    customer_name = Column(String(255), nullable=True)
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='SET NULL'), nullable=True)
    current_step = Column(String(50), nullable=False, default='location_request')
    latitude = Column(DECIMAL(10, 8), nullable=True)
    longitude = Column(DECIMAL(11, 8), nullable=True)
    location_timestamp = Column(DateTime(timezone=True), nullable=True)
    nearby_restaurants = Column(Text, nullable=True)  # JSON string (since JSONB not supported everywhere)
    cart = Column(Text, nullable=False, default='[]')  # JSON string
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'phone_number': self.phone_number,
            'customer_name': self.customer_name,
            'restaurant_id': self.restaurant_id,
            'current_step': self.current_step,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'location_timestamp': self.location_timestamp.isoformat() if self.location_timestamp else None,
            'nearby_restaurants': self.nearby_restaurants,
            'cart': self.cart,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
        }


class SubscriptionDB(Base):
    """Subscription model for database"""
    __tablename__ = 'subscriptions'
    
    id = Column(String(50), primary_key=True)
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='CASCADE'), unique=True, nullable=False)
    plan = Column(String(50), nullable=False, default='free')
    status = Column(String(20), nullable=False, default='active')
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    amount_paid = Column(DECIMAL(10, 2), nullable=False, default=0.00)
    payment_method = Column(String(50), nullable=True)
    auto_renew = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'plan': self.plan,
            'status': self.status,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'amount_paid': float(self.amount_paid),
            'payment_method': self.payment_method,
            'auto_renew': self.auto_renew,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class PaymentDB(Base):
    """Payment model for database"""
    __tablename__ = 'payments'
    
    id = Column(String(50), primary_key=True)
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='SET NULL'), nullable=True)
    order_id = Column(String(50), ForeignKey('orders.id', ondelete='SET NULL'), nullable=True)
    transaction_type = Column(String(20), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(String(50), nullable=False)
    payment_gateway = Column(String(50), nullable=True)
    transaction_id = Column(String(255), unique=True, nullable=True)
    status = Column(String(20), nullable=False, default='pending')
    customer_upi_name = Column(String(255), nullable=True)
    failure_reason = Column(Text, nullable=True)
    payment_metadata = Column('metadata', Text, nullable=True)  # JSON string (database column is 'metadata')
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'order_id': self.order_id,
            'transaction_type': self.transaction_type,
            'amount': float(self.amount),
            'payment_method': self.payment_method,
            'payment_gateway': self.payment_gateway,
            'transaction_id': self.transaction_id,
            'status': self.status,
            'customer_upi_name': self.customer_upi_name,
            'failure_reason': self.failure_reason,
            'metadata': self.payment_metadata,  # Return as 'metadata' in API response
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class RestaurantUPIQRCodeHistoryDB(Base):
    """SCD Type 2 History table for UPI QR code changes"""
    __tablename__ = 'restaurant_upi_qr_code_history'
    
    id = Column(String(50), primary_key=True)
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    upi_qr_code = Column(Text, nullable=False)
    version_number = Column(Integer, nullable=False)
    is_current = Column(Boolean, nullable=False, default=False)
    changed_by_user_id = Column(String(50), ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    change_reason = Column(String(255), nullable=True)
    effective_from = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    effective_to = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    restaurant = relationship("RestaurantDB", backref="qr_code_history")
    changed_by_user = relationship("UserDB", foreign_keys=[changed_by_user_id])
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'upi_qr_code': self.upi_qr_code,
            'version_number': self.version_number,
            'is_current': self.is_current,
            'changed_by_user_id': self.changed_by_user_id,
            'change_reason': self.change_reason,
            'effective_from': self.effective_from.isoformat() if self.effective_from else None,
            'effective_to': self.effective_to.isoformat() if self.effective_to else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


class RestaurantRatingDB(Base):
    """Restaurant rating cache model for database"""
    __tablename__ = 'restaurant_ratings'
    
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='CASCADE'), primary_key=True)
    overall_rating = Column(DECIMAL(3, 2), nullable=False, default=4.0)
    customer_rating = Column(DECIMAL(3, 2), nullable=True)
    completion_rate = Column(DECIMAL(5, 4), nullable=False, default=1.0)
    total_orders = Column(Integer, nullable=False, default=0)
    rated_orders = Column(Integer, nullable=False, default=0)
    delivered_orders = Column(Integer, nullable=False, default=0)
    cancelled_orders = Column(Integer, nullable=False, default=0)
    calculated_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'restaurant_id': self.restaurant_id,
            'overall_rating': float(self.overall_rating),
            'customer_rating': float(self.customer_rating) if self.customer_rating else None,
            'completion_rate': float(self.completion_rate),
            'total_orders': self.total_orders,
            'rated_orders': self.rated_orders,
            'delivered_orders': self.delivered_orders,
            'cancelled_orders': self.cancelled_orders,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
        }


class RestaurantNotificationDB(Base):
    """Restaurant Notification model for database"""
    __tablename__ = 'restaurant_notifications'
    
    id = Column(String(50), primary_key=True)
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False)
    order_id = Column(String(50), ForeignKey('orders.id', ondelete='SET NULL'), nullable=True)
    notification_type = Column(String(20), nullable=False)  # 'whatsapp', 'email', 'sms'
    notification_event = Column(String(50), nullable=False)  # 'new_order', 'order_status_changed', etc.
    recipient = Column(String(255), nullable=False)  # phone number, email, etc.
    message_body = Column(Text, nullable=False)
    status = Column(String(20), nullable=False, default='sent')  # 'sent', 'delivered', 'failed', 'clicked'
    button_clicked = Column(String(50), nullable=True)  # 'accept', 'preparing', 'ready', 'cancel', etc.
    clicked_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    restaurant = relationship("RestaurantDB", backref="notifications")
    order = relationship("OrderDB", backref="notifications")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'order_id': self.order_id,
            'notification_type': self.notification_type,
            'notification_event': self.notification_event,
            'recipient': self.recipient,
            'message_body': self.message_body,
            'status': self.status,
            'button_clicked': self.button_clicked,
            'clicked_at': self.clicked_at.isoformat() if self.clicked_at else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class RestaurantSettingsDB(Base):
    """Restaurant Settings Database Model"""
    __tablename__ = 'restaurant_settings'
    
    id = Column(String(50), primary_key=True)
    restaurant_id = Column(String(50), ForeignKey('restaurants.id', ondelete='CASCADE'), nullable=False, unique=True)
    
    # Notification Settings
    whatsapp_notifications_enabled = Column(Boolean, nullable=False, default=True)
    whatsapp_number = Column(String(20), nullable=True)
    email_notifications_enabled = Column(Boolean, nullable=False, default=False)
    email_address = Column(String(255), nullable=True)
    sms_notifications_enabled = Column(Boolean, nullable=False, default=False)
    sms_number = Column(String(20), nullable=True)
    
    # Notification Preferences
    notify_new_order = Column(Boolean, nullable=False, default=True)
    notify_preparing = Column(Boolean, nullable=False, default=True)
    notify_ready = Column(Boolean, nullable=False, default=True)
    notify_delivered = Column(Boolean, nullable=False, default=True)
    notify_cancelled = Column(Boolean, nullable=False, default=True)
    notify_payment = Column(Boolean, nullable=False, default=True)
    
    # UI Preferences
    sound_enabled = Column(Boolean, nullable=False, default=True)
    blink_enabled = Column(Boolean, nullable=False, default=True)
    
    # Order Settings
    auto_accept_orders = Column(Boolean, nullable=False, default=False)
    default_preparation_time = Column(Integer, nullable=False, default=30)
    minimum_order_value = Column(DECIMAL(10, 2), nullable=False, default=0.0)
    maximum_order_value = Column(DECIMAL(10, 2), nullable=True)
    allow_order_modifications = Column(Boolean, nullable=False, default=True)
    cancellation_policy = Column(Text, nullable=True)
    delivery_available = Column(Boolean, nullable=False, default=True)  # Whether delivery option is available

    # Profile / Business Settings
    delivery_radius_km = Column(Integer, nullable=True)
    gst_number = Column(String(50), nullable=True)
    pan_number = Column(String(20), nullable=True)
    fssai_number = Column(String(50), nullable=True)
    operating_hours = Column(Text, nullable=True)  # JSON string of weekly schedule
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    restaurant = relationship("RestaurantDB", backref="settings")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'restaurant_id': self.restaurant_id,
            'whatsapp_notifications_enabled': self.whatsapp_notifications_enabled,
            'whatsapp_number': self.whatsapp_number,
            'email_notifications_enabled': self.email_notifications_enabled,
            'email_address': self.email_address,
            'sms_notifications_enabled': self.sms_notifications_enabled,
            'sms_number': self.sms_number,
            'notify_new_order': self.notify_new_order,
            'notify_preparing': self.notify_preparing,
            'notify_ready': self.notify_ready,
            'notify_delivered': self.notify_delivered,
            'notify_cancelled': self.notify_cancelled,
            'notify_payment': self.notify_payment,
            'sound_enabled': self.sound_enabled,
            'blink_enabled': self.blink_enabled,
            'auto_accept_orders': self.auto_accept_orders,
            'default_preparation_time': self.default_preparation_time,
            'minimum_order_value': float(self.minimum_order_value) if self.minimum_order_value else 0.0,
            'maximum_order_value': float(self.maximum_order_value) if self.maximum_order_value else None,
            'allow_order_modifications': self.allow_order_modifications,
            'cancellation_policy': self.cancellation_policy,
            'delivery_radius_km': self.delivery_radius_km,
            'gst_number': self.gst_number,
            'pan_number': self.pan_number,
            'fssai_number': self.fssai_number,
            'operating_hours': self.operating_hours,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class DeliveryPersonDB(Base):
    """Delivery Person model for database"""
    __tablename__ = 'delivery_persons'
    
    id = Column(String(50), primary_key=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    vehicle_type = Column(String(20), nullable=False, default='bike')
    license_number = Column(String(100), nullable=True)
    is_available = Column(Boolean, nullable=False, default=False)
    current_latitude = Column(DECIMAL(10, 8), nullable=True)
    current_longitude = Column(DECIMAL(11, 8), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'password_hash': self.password_hash,
            'vehicle_type': self.vehicle_type,
            'license_number': self.license_number,
            'is_available': self.is_available,
            'current_latitude': float(self.current_latitude) if self.current_latitude else None,
            'current_longitude': float(self.current_longitude) if self.current_longitude else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
