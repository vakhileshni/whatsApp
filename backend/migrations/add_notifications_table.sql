-- Notifications Tracking Table
-- Tracks all notifications sent to restaurant owners (WhatsApp, Email, SMS)

CREATE TABLE IF NOT EXISTS restaurant_notifications (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) NOT NULL,
    order_id VARCHAR(50) NULL,  -- NULL for non-order notifications
    notification_type VARCHAR(20) NOT NULL,  -- 'whatsapp', 'email', 'sms'
    notification_event VARCHAR(50) NOT NULL,  -- 'new_order', 'order_status_changed', 'payment_received', etc.
    recipient VARCHAR(255) NOT NULL,  -- phone number, email, etc.
    message_body TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'sent',  -- 'sent', 'delivered', 'failed', 'clicked'
    button_clicked VARCHAR(50) NULL,  -- 'accept', 'preparing', 'ready', 'cancel', etc.
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

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_notifications_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_notifications_updated_at ON restaurant_notifications;
CREATE TRIGGER update_notifications_updated_at BEFORE UPDATE ON restaurant_notifications 
FOR EACH ROW EXECUTE FUNCTION update_notifications_updated_at_column();
