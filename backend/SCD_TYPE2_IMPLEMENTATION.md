# SCD Type 2 Implementation for UPI QR Code

## Overview
This document describes the Slowly Changing Dimension (SCD) Type 2 implementation for tracking UPI QR code changes over time.

## What is SCD Type 2?

SCD Type 2 maintains a complete history of changes by:
- **Keeping all versions** of the QR code
- **Tracking effective dates** (when each version was active)
- **Version numbering** for easy reference
- **Automatic history creation** via database triggers
- **Ability to revert** to previous versions

## Database Schema

### History Table: `restaurant_upi_qr_code_history`

```sql
CREATE TABLE restaurant_upi_qr_code_history (
    id VARCHAR(50) PRIMARY KEY,
    restaurant_id VARCHAR(50) NOT NULL,
    upi_qr_code TEXT NOT NULL,
    version_number INT NOT NULL,
    is_current BOOLEAN NOT NULL DEFAULT FALSE,
    changed_by_user_id VARCHAR(50) NULL,
    change_reason VARCHAR(255) NULL,
    effective_from TIMESTAMP NOT NULL,
    effective_to TIMESTAMP NULL,
    created_at TIMESTAMP NOT NULL
);
```

### Key Fields:
- **`version_number`**: Sequential version (1, 2, 3, ...)
- **`is_current`**: TRUE for the most recent version
- **`effective_from`**: When this version became active
- **`effective_to`**: When this version was replaced (NULL for current)

## How It Works

### 1. Automatic History Creation
When a QR code is updated in the `restaurants` table:
1. Database trigger fires automatically
2. Previous version is marked as `is_current = FALSE` and `effective_to` is set
3. New version is inserted with `is_current = TRUE` and `effective_from = NOW()`
4. Version number is auto-incremented

### 2. Current QR Code
The current QR code is stored in:
- **`restaurants.upi_qr_code`** (for fast access)
- **`restaurant_upi_qr_code_history`** with `is_current = TRUE` (for history tracking)

### 3. Querying History

```sql
-- Get all versions
SELECT * FROM restaurant_upi_qr_code_history
WHERE restaurant_id = '000000010'
ORDER BY version_number DESC;

-- Get current version
SELECT * FROM restaurant_upi_qr_code_history
WHERE restaurant_id = '000000010' AND is_current = TRUE;

-- Get specific version
SELECT * FROM restaurant_upi_qr_code_history
WHERE restaurant_id = '000000010' AND version_number = 3;
```

## API Endpoints

### Get History
```
GET /api/v1/dashboard/restaurant/upi/qr-code/history?limit=10
```
Returns list of all QR code versions with timestamps.

### Revert to Version
```
POST /api/v1/dashboard/restaurant/upi/qr-code/revert/{version_number}
```
Reverts QR code to a previous version (creates new history entry).

## Database Functions

### `get_next_qr_code_version(restaurant_id)`
Returns the next version number for a restaurant.

### `handle_upi_qr_code_scd_update()`
Trigger function that automatically creates history entries.

### `revert_qr_code_to_version(restaurant_id, version_number)`
Reverts QR code to a specific version.

## Benefits

1. **Complete Audit Trail**: Every change is tracked with timestamp
2. **Data Recovery**: Can revert to any previous version
3. **Compliance**: Meets data retention and audit requirements
4. **Analytics**: Can analyze how often QR codes change
5. **Debugging**: Can see what QR code was active at any point in time

## Performance Considerations

- **Indexes**: Optimized for common queries
  - `restaurant_id` + `version_number`
  - `restaurant_id` + `is_current`
  - `effective_from` + `effective_to`
  
- **Storage**: History table can grow large over time
  - Consider archiving old versions (>1 year)
  - Or implement retention policy

## Migration

To apply the SCD Type 2 implementation:

```bash
cd backend
python run_scd_migration.py
```

Or manually run:
```bash
psql -d whatsapp_db -f migrations/add_upi_qr_code_history.sql
```

## Example Usage

### Scenario: Restaurant updates QR code 3 times

1. **Initial Upload** (Version 1)
   - `effective_from`: 2024-01-01 10:00:00
   - `effective_to`: NULL
   - `is_current`: TRUE

2. **First Update** (Version 2)
   - Version 1: `effective_to` = 2024-01-15 14:30:00, `is_current` = FALSE
   - Version 2: `effective_from` = 2024-01-15 14:30:00, `is_current` = TRUE

3. **Second Update** (Version 3)
   - Version 2: `effective_to` = 2024-02-01 09:00:00, `is_current` = FALSE
   - Version 3: `effective_from` = 2024-02-01 09:00:00, `is_current` = TRUE

### Query: What QR code was active on Jan 20?
```sql
SELECT upi_qr_code, version_number
FROM restaurant_upi_qr_code_history
WHERE restaurant_id = '000000010'
  AND effective_from <= '2024-01-20'
  AND (effective_to IS NULL OR effective_to > '2024-01-20')
ORDER BY version_number DESC
LIMIT 1;
```
Result: Version 2 (active from Jan 15 to Feb 1)

## Maintenance

### Archive Old Versions
```sql
-- Mark versions older than 1 year as archived
UPDATE restaurant_upi_qr_code_history
SET is_current = FALSE
WHERE effective_to < NOW() - INTERVAL '1 year'
  AND is_current = TRUE;
```

### Cleanup (Optional)
```sql
-- Delete versions older than 2 years (if needed)
DELETE FROM restaurant_upi_qr_code_history
WHERE effective_to < NOW() - INTERVAL '2 years'
  AND is_current = FALSE;
```

## Testing

Test the SCD implementation:

```python
from repositories.qr_code_history_repo import get_qr_code_history, revert_to_version

# Get history
history = get_qr_code_history('000000010', limit=10)
print(f"Total versions: {len(history)}")

# Revert to version 1
success = revert_to_version('000000010', 1)
print(f"Revert successful: {success}")
```
