"""
User model - Pure data structure
"""
from dataclasses import dataclass

@dataclass
class User:
    """Restaurant admin user"""
    id: str
    email: str
    password: str  # Plain text for demo (use hashing in production)
    restaurant_id: str
    name: str
    two_factor_enabled: bool = False
    two_factor_secret: str = ""  # TOTP secret key
    two_factor_backup_codes: str = ""  # JSON array of backup codes


