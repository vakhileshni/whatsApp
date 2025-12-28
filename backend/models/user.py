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


