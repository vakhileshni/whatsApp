"""
QR Code Decoder Service
Extracts UPI ID from QR code images
"""
import logging
import base64
import re
import urllib.parse
from io import BytesIO
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

# Try OpenCV first (works on Windows without DLL dependencies)
QR_DECODER_AVAILABLE = False
QR_DECODER_METHOD = None

try:
    import cv2
    import numpy as np
    QR_DECODER_AVAILABLE = True
    QR_DECODER_METHOD = "opencv"
    logger.info("✅ Using OpenCV for QR code decoding (works on Windows)")
except ImportError:
    logger.warning("OpenCV not available. Trying pyzbar...")

# Try pyzbar as fallback (requires DLLs on Windows)
if not QR_DECODER_AVAILABLE:
    try:
        from PIL import Image
        from pyzbar import pyzbar
        QR_DECODER_AVAILABLE = True
        QR_DECODER_METHOD = "pyzbar"
        logger.info("✅ Using pyzbar for QR code decoding")
    except (ImportError, OSError, FileNotFoundError) as e:
        logger.warning(f"pyzbar not available (may need DLLs on Windows): {e}")
        if not QR_DECODER_AVAILABLE:
            logger.error("❌ No QR decoder available. Install opencv-python-headless or pyzbar with DLLs.")


def decode_qr_code_from_base64(base64_data: str) -> Optional[str]:
    """
    Decode QR code from base64 image data URL
    
    Args:
        base64_data: Base64 encoded image (with or without data URL prefix)
        
    Returns:
        Decoded QR code string (e.g., "upi://pay?pa=...") or None if decoding fails
    """
    if not QR_DECODER_AVAILABLE:
        logger.error("QR decoder libraries not available")
        return None
    
    try:
        # Remove data URL prefix if present (e.g., "data:image/png;base64,")
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
        
        # Decode base64 to image bytes
        image_bytes = base64.b64decode(base64_data)
        
        # Try OpenCV first (works on Windows without DLL dependencies)
        if QR_DECODER_METHOD == "opencv":
            try:
                import cv2
                import numpy as np
                
                # Decode image with OpenCV
                nparr = np.frombuffer(image_bytes, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is None:
                    logger.warning("Failed to decode image with OpenCV")
                else:
                    # Use OpenCV QRCodeDetector
                    detector = cv2.QRCodeDetector()
                    retval, decoded_info, points, straight_qrcode = detector.detectAndDecodeMulti(img)
                    
                    if retval and decoded_info:
                        qr_data = decoded_info[0]
                        logger.info(f"✅ Successfully decoded QR code with OpenCV: {qr_data[:50]}...")
                        return qr_data
                    else:
                        logger.warning("OpenCV detected QR code but couldn't decode it")
            except ImportError:
                logger.error("OpenCV not available")
            except Exception as e:
                logger.error(f"OpenCV decoding failed: {e}", exc_info=True)
        
        # Try pyzbar as fallback (requires DLLs on Windows)
        if QR_DECODER_METHOD == "pyzbar":
            try:
                from PIL import Image
                from pyzbar import pyzbar
                
                # Open image with PIL
                image = Image.open(BytesIO(image_bytes))
                
                # Convert to RGB if necessary (pyzbar requires RGB)
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Decode QR code
                decoded_objects = pyzbar.decode(image)
                
                if decoded_objects:
                    qr_data = decoded_objects[0].data.decode('utf-8')
                    logger.info(f"✅ Successfully decoded QR code with pyzbar: {qr_data[:50]}...")
                    return qr_data
            except (ImportError, OSError, FileNotFoundError) as e:
                logger.warning(f"pyzbar not available (may need DLLs): {e}")
            except Exception as e:
                logger.warning(f"pyzbar decoding failed: {e}")
        
        logger.warning("No QR code found in image with any decoder")
        return None
        
    except Exception as e:
        logger.error(f"❌ Failed to decode QR code: {e}", exc_info=True)
        return None


def extract_upi_id_from_qr_string(qr_string: str) -> Optional[str]:
    """
    Extract UPI ID from QR code string
    
    Args:
        qr_string: Decoded QR code string (e.g., "upi://pay?pa=name@upi&pn=...")
        
    Returns:
        UPI ID (e.g., "name@upi") or None if not found
    """
    try:
        # Check if it's a UPI payment string
        if not qr_string.startswith('upi://'):
            logger.warning(f"QR code is not a UPI payment string: {qr_string[:50]}")
            return None
        
        # Parse UPI URL
        # Format: upi://pay?pa=<UPI_ID>&pn=<Payee Name>&am=<Amount>&cu=INR&tn=<Transaction Note>
        if '?' in qr_string:
            query_string = qr_string.split('?', 1)[1]
            params = urllib.parse.parse_qs(query_string)
            
            # Extract 'pa' parameter (Payment Address = UPI ID)
            if 'pa' in params and params['pa']:
                upi_id = params['pa'][0]
                # Decode URL encoding
                upi_id = urllib.parse.unquote(upi_id)
                logger.info(f"✅ Extracted UPI ID: {upi_id}")
                return upi_id
        
        # Alternative: Try regex extraction
        match = re.search(r'pa=([^&]+)', qr_string)
        if match:
            upi_id = urllib.parse.unquote(match.group(1))
            logger.info(f"✅ Extracted UPI ID via regex: {upi_id}")
            return upi_id
        
        logger.warning(f"Could not extract UPI ID from QR string: {qr_string[:100]}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Failed to extract UPI ID: {e}")
        return None


def decode_qr_and_extract_upi_id(qr_code_data: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Decode QR code image and extract UPI ID
    
    Args:
        qr_code_data: Base64 encoded QR code image or URL
        
    Returns:
        Tuple of (decoded_qr_string, extracted_upi_id)
        Returns (None, None) if decoding fails
    """
    # If it's a URL, we can't decode it directly
    if qr_code_data.startswith('http://') or qr_code_data.startswith('https://'):
        logger.warning("QR code is a URL, cannot decode directly. Please upload as base64 image.")
        return None, None
    
    # Decode QR code
    qr_string = decode_qr_code_from_base64(qr_code_data)
    if not qr_string:
        return None, None
    
    # Extract UPI ID
    upi_id = extract_upi_id_from_qr_string(qr_string)
    
    return qr_string, upi_id
