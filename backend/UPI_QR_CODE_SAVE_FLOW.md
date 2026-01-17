# UPI QR Code Save Flow - Database Integration

## Overview
This document explains how UPI QR codes are saved to the database when uploaded through the Settings page.

## Database Schema

### Table: `restaurants`
```sql
CREATE TABLE restaurants (
    ...
    upi_qr_code TEXT DEFAULT '',
    ...
);
```

The `upi_qr_code` column stores:
- Base64 encoded image data (format: `data:image/png;base64,...`)
- OR URL to QR code image (format: `https://api.qrserver.com/...`)

## Complete Flow

### 1. Frontend - User Uploads QR Code
**File:** `frontend/app/dashboard/settings/page.tsx`

```typescript
handleQrCodeFileChange() {
  // User selects image file
  // FileReader converts to base64
  // Format: "data:image/png;base64,iVBORw0KG..."
  setUpiQrCode(base64);
}
```

### 2. Frontend - User Clicks Save
**File:** `frontend/app/dashboard/settings/page.tsx`

```typescript
handleSaveQrCode() {
  // Validates QR code format
  // Calls API: apiClient.saveUPIQRCode(upiQrCode)
  // Updates UI on success
}
```

### 3. Frontend API Client
**File:** `frontend/lib/api.ts`

```typescript
saveUPIQRCode(upi_qr_code: string) {
  // POST /api/v1/dashboard/restaurant/upi/qr-code
  // Body: { upi_qr_code: "data:image/..." }
  // Returns: RestaurantInfo with saved QR code
}
```

### 4. Backend API Endpoint
**File:** `backend/routers/dashboard.py`

```python
@router.post("/restaurant/upi/qr-code")
async def save_upi_qr_code(qr_request: SaveUPIQRCodeRequest):
    # 1. Authenticate user
    # 2. Get restaurant from database
    # 3. Verify user owns restaurant
    # 4. Validate QR code data
    # 5. Update restaurant.upi_qr_code
    # 6. Call update_restaurant() to save to DB
    # 7. Return updated restaurant info
```

### 5. Repository Layer - Database Update
**File:** `backend/repositories/restaurant_repo.py`

```python
def update_restaurant(restaurant: Restaurant):
    # 1. Get restaurant from DB
    # 2. Convert model to dict (includes upi_qr_code)
    # 3. Update all fields using setattr()
    # 4. Commit to database
    # 5. Return updated model
```

### 6. Model Converter
**File:** `backend/model_converters.py`

```python
def restaurant_model_to_db(model: Restaurant) -> dict:
    return {
        ...
        'upi_qr_code': model.upi_qr_code or '',
        ...
    }
```

### 7. Database Model
**File:** `backend/models_db.py`

```python
class RestaurantDB(Base):
    upi_qr_code = Column(Text, default='')
```

## Verification

The QR code is saved to PostgreSQL database in the `restaurants` table, `upi_qr_code` column.

### To Verify:
1. Check database:
```sql
SELECT id, name, upi_id, 
       LENGTH(upi_qr_code) as qr_length,
       LEFT(upi_qr_code, 50) as qr_preview
FROM restaurants 
WHERE upi_qr_code != '';
```

2. Check logs:
- Backend logs show: "Successfully saved QR code for restaurant {id}"
- Frontend console shows: "QR code saved successfully"

## Error Handling

### Frontend:
- Validates QR code format before sending
- Shows user-friendly error messages
- Logs errors to console for debugging

### Backend:
- Validates user authentication
- Verifies restaurant ownership
- Validates QR code data format
- Logs all operations
- Returns detailed error messages

## Testing

The QR code save functionality has been tested and verified:
- ✅ Database column exists
- ✅ Save operation works
- ✅ Data persists in database
- ✅ Can be retrieved after save

## Usage

1. Go to **Settings → Payments** tab
2. Upload QR code image OR generate from UPI ID
3. Click **"Save QR Code"** button
4. QR code is saved to database
5. QR code appears when customers click "UPI" button on Dashboard

## Notes

- QR codes can be up to several MB (stored as TEXT in PostgreSQL)
- Base64 encoding increases size by ~33%
- For large QR codes, consider storing as URL instead of base64
- QR code is loaded automatically when Settings page opens
