"""
Test script to verify QR decoder is working
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
print("Testing QR decoder imports...")
try:
    from services.qr_decoder import decode_qr_and_extract_upi_id, QR_DECODER_AVAILABLE, QR_DECODER_METHOD
    print("QR decoder module imported successfully")
    print(f"   - QR_DECODER_AVAILABLE: {QR_DECODER_AVAILABLE}")
    print(f"   - QR_DECODER_METHOD: {QR_DECODER_METHOD}")
except ImportError as e:
    print(f"Failed to import QR decoder: {e}")
    sys.exit(1)

# Test with a sample UPI QR code string (not image, just the decoded string)
print("\nTesting UPI ID extraction from QR string...")
test_qr_string = "upi://pay?pa=test@paytm&pn=Test%20Restaurant&am=100.00&cu=INR&tn=Order%20Payment"
from services.qr_decoder import extract_upi_id_from_qr_string

upi_id = extract_upi_id_from_qr_string(test_qr_string)
if upi_id:
    print(f"Successfully extracted UPI ID: {upi_id}")
else:
    print(f"Failed to extract UPI ID from test string")

print("\nQR decoder test complete!")
print("\nTo test with actual QR image:")
print("   1. Upload a QR code via the frontend")
print("   2. Check backend logs for decoder output")
