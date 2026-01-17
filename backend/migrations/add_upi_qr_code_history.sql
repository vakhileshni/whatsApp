-- SCD Type 2 Implementation for UPI QR Code Changes
-- This migration adds history tracking for UPI QR code changes

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
    v_user_id VARCHAR(50);
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

-- Function to get current QR code version
CREATE OR REPLACE FUNCTION get_current_qr_code_version(p_restaurant_id VARCHAR(50))
RETURNS TABLE (
    id VARCHAR(50),
    restaurant_id VARCHAR(50),
    upi_qr_code TEXT,
    version_number INT,
    effective_from TIMESTAMP,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.id,
        h.restaurant_id,
        h.upi_qr_code,
        h.version_number,
        h.effective_from,
        h.created_at
    FROM restaurant_upi_qr_code_history h
    WHERE h.restaurant_id = p_restaurant_id
      AND h.is_current = TRUE
    ORDER BY h.version_number DESC
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;

-- Function to get all versions for a restaurant
CREATE OR REPLACE FUNCTION get_qr_code_history(p_restaurant_id VARCHAR(50), p_limit INT DEFAULT 10)
RETURNS TABLE (
    id VARCHAR(50),
    restaurant_id VARCHAR(50),
    upi_qr_code TEXT,
    version_number INT,
    is_current BOOLEAN,
    effective_from TIMESTAMP,
    effective_to TIMESTAMP,
    created_at TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        h.id,
        h.restaurant_id,
        h.upi_qr_code,
        h.version_number,
        h.is_current,
        h.effective_from,
        h.effective_to,
        h.created_at
    FROM restaurant_upi_qr_code_history h
    WHERE h.restaurant_id = p_restaurant_id
    ORDER BY h.version_number DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

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

-- Migrate existing QR codes to history (one-time migration)
DO $$
DECLARE
    r RECORD;
    v_version INT;
BEGIN
    FOR r IN 
        SELECT id, upi_qr_code 
        FROM restaurants 
        WHERE upi_qr_code IS NOT NULL AND upi_qr_code != ''
    LOOP
        -- Check if history already exists
        IF NOT EXISTS (
            SELECT 1 FROM restaurant_upi_qr_code_history 
            WHERE restaurant_id = r.id
        ) THEN
            -- Insert initial version
            INSERT INTO restaurant_upi_qr_code_history (
                id,
                restaurant_id,
                upi_qr_code,
                version_number,
                is_current,
                effective_from,
                created_at
            ) VALUES (
                'qr_hist_' || r.id || '_000001',
                r.id,
                r.upi_qr_code,
                1,
                TRUE,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP
            );
        END IF;
    END LOOP;
END $$;

COMMENT ON TABLE restaurant_upi_qr_code_history IS 'SCD Type 2 history table for tracking UPI QR code changes over time';
COMMENT ON COLUMN restaurant_upi_qr_code_history.version_number IS 'Sequential version number for this restaurant';
COMMENT ON COLUMN restaurant_upi_qr_code_history.is_current IS 'TRUE for the most recent version, FALSE for historical versions';
COMMENT ON COLUMN restaurant_upi_qr_code_history.effective_from IS 'When this version became active';
COMMENT ON COLUMN restaurant_upi_qr_code_history.effective_to IS 'When this version was replaced (NULL for current version)';
