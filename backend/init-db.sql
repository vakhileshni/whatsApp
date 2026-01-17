-- Database Initialization Script for WhatsApp Business Ordering System
-- PostgreSQL Database Schema
-- This script creates all required tables

-- Enable UUID extension (if needed)
-- CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Restaurants Table (must be created first as other tables reference it)
CREATE TABLE IF NOT EXISTS restaurants (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    delivery_fee DECIMAL(10, 2) NOT NULL DEFAULT 40.00,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    upi_id VARCHAR(255) DEFAULT '',
    upi_password VARCHAR(255) DEFAULT '',
    upi_qr_code TEXT DEFAULT '',
    cuisine_type VARCHAR(50) NOT NULL DEFAULT 'both',
    subscription_plan VARCHAR(50) DEFAULT 'free',
    subscription_end_date DATE NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_restaurants_is_active ON restaurants(is_active);
CREATE INDEX IF NOT EXISTS idx_restaurants_subscription_plan ON restaurants(subscription_plan);

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    restaurant_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    last_login TIMESTAMP NULL,
    -- Multi-Factor Authentication (MFA)
    two_factor_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    two_factor_secret VARCHAR(255) NULL,
    two_factor_backup_codes TEXT NULL,
    CONSTRAINT fk_users_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_users_restaurant_id ON users(restaurant_id);

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    price DECIMAL(10, 2) NOT NULL,
    discounted_price DECIMAL(10, 2) NULL,
    discount_percentage DECIMAL(5, 2) NULL,
    category VARCHAR(100) NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    image_url VARCHAR(500) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_products_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_products_restaurant_id ON products(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
CREATE INDEX IF NOT EXISTS idx_products_is_available ON products(is_available);
CREATE INDEX IF NOT EXISTS idx_products_restaurant_category ON products(restaurant_id, category);

-- Customers Table
CREATE TABLE IF NOT EXISTS customers (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(255) NULL,
    latitude DECIMAL(10, 8) DEFAULT 0.0,
    longitude DECIMAL(11, 8) DEFAULT 0.0,
    last_location_update TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_customers_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_customers_restaurant_id ON customers(restaurant_id);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) NOT NULL,
    customer_id VARCHAR(50) NOT NULL,
    customer_phone VARCHAR(20) NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    order_type VARCHAR(20) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    delivery_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    subtotal DECIMAL(10, 2) NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(20) NOT NULL DEFAULT 'cod',
    payment_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    customer_upi_name VARCHAR(255) NULL,
    delivery_address TEXT NULL,
    customer_rating DECIMAL(3, 2) NULL,
    notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_orders_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE,
    CONSTRAINT chk_customer_rating CHECK (customer_rating IS NULL OR (customer_rating >= 1 AND customer_rating <= 5))
);

CREATE INDEX IF NOT EXISTS idx_orders_restaurant_id ON orders(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_orders_payment_status ON orders(payment_status);
CREATE INDEX IF NOT EXISTS idx_orders_created_at ON orders(created_at);
CREATE INDEX IF NOT EXISTS idx_orders_restaurant_status ON orders(restaurant_id, status);
CREATE INDEX IF NOT EXISTS idx_orders_customer_created ON orders(customer_id, created_at);

-- Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    id VARCHAR(50) PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    price DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_order_items_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    CONSTRAINT fk_order_items_product FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
);

CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_order_items_order_product ON order_items(order_id, product_id);

-- Customer Sessions Table
CREATE TABLE IF NOT EXISTS customer_sessions (
    phone_number VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(255) NULL,
    restaurant_id VARCHAR(50) NULL,
    current_step VARCHAR(50) NOT NULL DEFAULT 'location_request',
    latitude DECIMAL(10, 8) NULL,
    longitude DECIMAL(11, 8) NULL,
    location_timestamp TIMESTAMP NULL,
    nearby_restaurants JSONB NULL,
    cart JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NULL,
    CONSTRAINT fk_sessions_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_restaurant_id ON customer_sessions(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_sessions_expires_at ON customer_sessions(expires_at);

-- Subscriptions Table
CREATE TABLE IF NOT EXISTS subscriptions (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) UNIQUE NOT NULL,
    plan VARCHAR(50) NOT NULL DEFAULT 'free',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    start_date DATE NOT NULL,
    end_date DATE NULL,
    amount_paid DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_method VARCHAR(50) NULL,
    auto_renew BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_subscriptions_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_subscriptions_status ON subscriptions(status);
CREATE INDEX IF NOT EXISTS idx_subscriptions_end_date ON subscriptions(end_date);
CREATE INDEX IF NOT EXISTS idx_subscriptions_plan ON subscriptions(plan);

-- Payments/Transactions Table
CREATE TABLE IF NOT EXISTS payments (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) NULL,
    order_id VARCHAR(50) NULL,
    transaction_type VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_gateway VARCHAR(50) NULL,
    transaction_id VARCHAR(255) UNIQUE NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    customer_upi_name VARCHAR(255) NULL,
    failure_reason TEXT NULL,
    metadata JSONB NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_payments_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE SET NULL,
    CONSTRAINT fk_payments_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_payments_restaurant_id ON payments(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_payments_order_id ON payments(order_id);
CREATE INDEX IF NOT EXISTS idx_payments_status ON payments(status);
CREATE INDEX IF NOT EXISTS idx_payments_created_at ON payments(created_at);
CREATE INDEX IF NOT EXISTS idx_payments_type_status ON payments(transaction_type, status);

-- Restaurant Ratings Cache Table
CREATE TABLE IF NOT EXISTS restaurant_ratings (
    restaurant_id VARCHAR(50) PRIMARY KEY,
    overall_rating DECIMAL(3, 2) NOT NULL DEFAULT 4.0,
    customer_rating DECIMAL(3, 2) NULL,
    completion_rate DECIMAL(5, 4) NOT NULL DEFAULT 1.0,
    total_orders INT NOT NULL DEFAULT 0,
    rated_orders INT NOT NULL DEFAULT 0,
    delivered_orders INT NOT NULL DEFAULT 0,
    cancelled_orders INT NOT NULL DEFAULT 0,
    calculated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_ratings_restaurant FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_ratings_overall_rating ON restaurant_ratings(overall_rating);
CREATE INDEX IF NOT EXISTS idx_ratings_calculated_at ON restaurant_ratings(calculated_at);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers for updated_at columns
CREATE TRIGGER update_restaurants_updated_at BEFORE UPDATE ON restaurants FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON products FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customers_updated_at BEFORE UPDATE ON customers FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_orders_updated_at BEFORE UPDATE ON orders FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_customer_sessions_updated_at BEFORE UPDATE ON customer_sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- SCD Type 2: UPI QR Code History Table
-- ============================================
-- History Table for UPI QR Code (SCD Type 2)
CREATE TABLE IF NOT EXISTS restaurant_upi_qr_code_history (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) NOT NULL,
    upi_qr_code TEXT NOT NULL,
    version_number INT NOT NULL,
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    changed_by_user_id VARCHAR(50) NULL,
    change_reason VARCHAR(255) NULL,
    effective_from TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    effective_to TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_qr_history_restaurant FOREIGN KEY (restaurant_id) 
        REFERENCES restaurants(id) ON DELETE CASCADE,
    CONSTRAINT fk_qr_history_user FOREIGN KEY (changed_by_user_id) 
        REFERENCES users(id) ON DELETE SET NULL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_qr_history_restaurant_id ON restaurant_upi_qr_code_history(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_qr_history_version ON restaurant_upi_qr_code_history(restaurant_id, version_number);
CREATE INDEX IF NOT EXISTS idx_qr_history_current ON restaurant_upi_qr_code_history(restaurant_id, is_current) WHERE is_current = TRUE;
CREATE INDEX IF NOT EXISTS idx_qr_history_effective_dates ON restaurant_upi_qr_code_history(restaurant_id, effective_from, effective_to);
CREATE INDEX IF NOT EXISTS idx_qr_history_created_at ON restaurant_upi_qr_code_history(created_at);

-- Function to get next version number for a restaurant
CREATE OR REPLACE FUNCTION get_next_qr_code_version(p_restaurant_id VARCHAR(50))
RETURNS INT AS $$
DECLARE
    v_max_version INT;
BEGIN
    SELECT COALESCE(MAX(version_number), 0) INTO v_max_version
    FROM restaurant_upi_qr_code_history
    WHERE restaurant_id = p_restaurant_id;
    
    RETURN v_max_version + 1;
END;
$$ LANGUAGE plpgsql;

-- Function to handle SCD Type 2 update
CREATE OR REPLACE FUNCTION handle_upi_qr_code_scd_update()
RETURNS TRIGGER AS $$
DECLARE
    v_old_qr_code TEXT;
    v_new_qr_code TEXT;
    v_next_version INT;
BEGIN
    -- Get old and new QR code values
    v_old_qr_code := OLD.upi_qr_code;
    v_new_qr_code := NEW.upi_qr_code;
    
    -- Only create history entry if QR code actually changed
    IF v_old_qr_code IS DISTINCT FROM v_new_qr_code AND v_new_qr_code != '' THEN
        -- Get next version number
        v_next_version := get_next_qr_code_version(NEW.id);
        
        -- Set effective_to for previous current version
        UPDATE restaurant_upi_qr_code_history
        SET is_current = FALSE,
            effective_to = CURRENT_TIMESTAMP
        WHERE restaurant_id = NEW.id
          AND is_current = TRUE;
        
        -- Insert new history record
        INSERT INTO restaurant_upi_qr_code_history (
            id,
            restaurant_id,
            upi_qr_code,
            version_number,
            is_current,
            effective_from,
            effective_to,
            created_at
        ) VALUES (
            'qr_hist_' || NEW.id || '_' || LPAD(v_next_version::TEXT, 6, '0'),
            NEW.id,
            v_new_qr_code,
            v_next_version,
            TRUE,
            CURRENT_TIMESTAMP,
            NULL,
            CURRENT_TIMESTAMP
        );
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to automatically create history on QR code update
DROP TRIGGER IF EXISTS trigger_upi_qr_code_scd_update ON restaurants;
CREATE TRIGGER trigger_upi_qr_code_scd_update
    AFTER UPDATE OF upi_qr_code ON restaurants
    FOR EACH ROW
    WHEN (OLD.upi_qr_code IS DISTINCT FROM NEW.upi_qr_code)
    EXECUTE FUNCTION handle_upi_qr_code_scd_update();

-- Function to revert to a previous version
CREATE OR REPLACE FUNCTION revert_qr_code_to_version(
    p_restaurant_id VARCHAR(50),
    p_version_number INT
)
RETURNS BOOLEAN AS $$
DECLARE
    v_qr_code TEXT;
BEGIN
    -- Get QR code from specified version
    SELECT h.upi_qr_code INTO v_qr_code
    FROM restaurant_upi_qr_code_history h
    WHERE h.restaurant_id = p_restaurant_id
      AND h.version_number = p_version_number;
    
    IF v_qr_code IS NULL THEN
        RETURN FALSE;
    END IF;
    
    -- Update restaurant with reverted QR code
    UPDATE restaurants
    SET upi_qr_code = v_qr_code
    WHERE id = p_restaurant_id;
    
    -- Trigger will automatically create new history entry
    
    RETURN TRUE;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- Restaurant Settings Table
-- ============================================
-- Stores notification preferences, order settings, and other restaurant configurations
CREATE TABLE IF NOT EXISTS restaurant_settings (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) NOT NULL UNIQUE,
    
    -- Notification Settings
    whatsapp_notifications_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    whatsapp_number VARCHAR(20) NULL,
    email_notifications_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    email_address VARCHAR(255) NULL,
    sms_notifications_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    sms_number VARCHAR(20) NULL,
    
    -- Notification Preferences
    notify_new_order BOOLEAN NOT NULL DEFAULT TRUE,
    notify_preparing BOOLEAN NOT NULL DEFAULT TRUE,
    notify_ready BOOLEAN NOT NULL DEFAULT TRUE,
    notify_delivered BOOLEAN NOT NULL DEFAULT TRUE,
    notify_cancelled BOOLEAN NOT NULL DEFAULT TRUE,
    notify_payment BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- UI Preferences
    sound_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    blink_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    
    -- Order Settings
    auto_accept_orders BOOLEAN NOT NULL DEFAULT FALSE,
    default_preparation_time INT NOT NULL DEFAULT 30,
    minimum_order_value DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    maximum_order_value DECIMAL(10, 2) NULL,
    allow_order_modifications BOOLEAN NOT NULL DEFAULT TRUE,
    cancellation_policy TEXT NULL,

    -- Profile / Business Settings
    delivery_radius_km INT NULL,
    gst_number VARCHAR(50) NULL,
    pan_number VARCHAR(20) NULL,
    fssai_number VARCHAR(50) NULL,
    operating_hours TEXT NULL,
    
    -- Timestamps
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_settings_restaurant FOREIGN KEY (restaurant_id) 
        REFERENCES restaurants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_settings_restaurant_id ON restaurant_settings(restaurant_id);

-- Function to update updated_at timestamp for settings
CREATE OR REPLACE FUNCTION update_settings_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at for settings
CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON restaurant_settings 
FOR EACH ROW EXECUTE FUNCTION update_settings_updated_at_column();

-- ============================================
-- Restaurant Notifications Table
-- ============================================
-- Tracks all notifications sent to restaurant owners (WhatsApp, Email, SMS)
CREATE TABLE IF NOT EXISTS restaurant_notifications (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NULL,
    notification_type VARCHAR(20) NOT NULL,
    notification_event VARCHAR(50) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    message_body TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'sent',
    button_clicked VARCHAR(50) NULL,
    clicked_at TIMESTAMP NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT fk_notifications_restaurant FOREIGN KEY (restaurant_id) 
        REFERENCES restaurants(id) ON DELETE CASCADE,
    CONSTRAINT fk_notifications_order FOREIGN KEY (order_id) 
        REFERENCES orders(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_notifications_restaurant_id ON restaurant_notifications(restaurant_id);
CREATE INDEX IF NOT EXISTS idx_notifications_order_id ON restaurant_notifications(order_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON restaurant_notifications(status);
CREATE INDEX IF NOT EXISTS idx_notifications_created_at ON restaurant_notifications(created_at);

-- Trigger to auto-update updated_at for notifications
CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON restaurant_notifications 
FOR EACH ROW EXECUTE FUNCTION update_settings_updated_at_column();

