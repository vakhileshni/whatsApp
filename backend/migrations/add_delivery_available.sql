-- Migration: Add delivery_available column to restaurant_settings table
-- This allows restaurants to enable/disable delivery option for customers

ALTER TABLE restaurant_settings 
ADD COLUMN IF NOT EXISTS delivery_available BOOLEAN NOT NULL DEFAULT TRUE;

-- Update existing records to have delivery_available = TRUE by default
UPDATE restaurant_settings 
SET delivery_available = TRUE 
WHERE delivery_available IS NULL;
