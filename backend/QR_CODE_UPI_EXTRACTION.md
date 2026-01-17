# QR Code UPI ID Automatic Extraction

## Overview
This feature automatically extracts the UPI ID from uploaded QR code images, eliminating the need for manual entry.

## How It Works

1. **QR Code Upload**: When a restaurant owner uploads a UPI QR code image via the dashboard settings, the backend receives it as a base64-encoded image.

2. **QR Code Decoding**: The system uses one of two methods to decode the QR code:
   - **Primary**: `pyzbar` library (requires zbar DLLs on Windows)
   - **Fallback**: `opencv-python-headless` library (works out of the box)

3. **UPI ID Extraction**: Once decoded, the system extracts the UPI ID from the QR code string:
   - Format: `upi://pay?pa=<UPI_ID>&pn=<Payee Name>&...`
   - Extracts the `pa` parameter (Payment Address = UPI ID)
   - URL-decodes the UPI ID

4. **Automatic Save**: The extracted UPI ID is automatically saved to `restaurants.upi_id` in the database.

## Implementation Details

### Files Modified
- `backend/services/qr_decoder.py` - New service for QR code decoding and UPI ID extraction
- `backend/routers/dashboard.py` - Updated `save_upi_qr_code` endpoint to automatically extract UPI ID
- `backend/requirements.txt` - Added dependencies: `Pillow`, `pyzbar`, `opencv-python-headless`

### API Endpoint
- `POST /api/v1/dashboard/restaurant/upi/qr-code`
  - Accepts: `SaveUPIQRCodeRequest` with `upi_qr_code` (base64 image)
  - Returns: `RestaurantInfo` with updated `upi_id` field
  - Automatically extracts and saves UPI ID if QR code is valid

### Error Handling
- If QR code decoding fails, the QR image is still saved, but UPI ID extraction is skipped
- Logs warnings/errors for debugging
- Falls back gracefully between decoding methods

## Dependencies

### Required Libraries
```bash
pip install Pillow pyzbar opencv-python-headless
```

### Windows Note
`pyzbar` requires zbar DLLs on Windows. If `pyzbar` fails, the system automatically falls back to OpenCV, which works without additional system dependencies.

## Usage

1. Go to Dashboard → Settings → UPI tab
2. Upload a UPI QR code image
3. The system automatically:
   - Saves the QR code image
   - Extracts the UPI ID from the QR code
   - Updates the `upi_id` field in the database
   - Displays the extracted UPI ID in the frontend

## Testing

To test the feature:
1. Upload a valid UPI QR code image
2. Check backend logs for:
   - `✅ Successfully decoded QR code with pyzbar/OpenCV`
   - `✅ Extracted UPI ID: <upi_id>`
   - `✅ UPI ID '<upi_id>' automatically extracted and saved`
3. Verify the UPI ID appears in the dashboard settings

## Troubleshooting

### QR Code Not Decoding
- Ensure the image is a valid QR code
- Check that the image format is supported (PNG, JPEG, etc.)
- Verify the QR code contains UPI payment data (`upi://pay?...`)

### UPI ID Not Extracted
- Check backend logs for decoding errors
- Verify the QR code format matches UPI payment standard
- Ensure the `pa` parameter exists in the QR code string

### Library Installation Issues
- On Windows, if `pyzbar` fails, OpenCV will be used automatically
- If both fail, check Python version compatibility
- Ensure all dependencies are installed: `pip install -r requirements.txt`
