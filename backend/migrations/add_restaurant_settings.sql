-- Restaurant Settings Table
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
    
    -- Notification Preferences (JSON)
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
    default_preparation_time INT NOT NULL DEFAULT 30, -- minutes
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

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_settings_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at (drop if exists first)
DROP TRIGGER IF EXISTS update_settings_updated_at ON restaurant_settings;
CREATE TRIGGER update_settings_updated_at BEFORE UPDATE ON restaurant_settings 
FOR EACH ROW EXECUTE FUNCTION update_settings_updated_at_column();
