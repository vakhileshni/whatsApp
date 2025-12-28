"""
Hardcoded users data - Acts like users table
"""
from models.user import User

USERS = {
    "user_001": User(
        id="user_001",
        email="admin@spicegarden.com",
        password="admin123",  # Demo password
        restaurant_id="rest_001",
        name="Admin Spice Garden"
    ),
    "user_002": User(
        id="user_002",
        email="admin@pizzaparadise.com",
        password="admin123",  # Demo password
        restaurant_id="rest_002",
        name="Admin Pizza Paradise"
    ),
    "user_003": User(
        id="user_003",
        email="admin@sushimasters.com",
        password="admin123",  # Demo password
        restaurant_id="rest_003",
        name="Admin Sushi Masters"
    ),
    "user_004": User(
        id="user_004",
        email="admin@burgerhub.com",
        password="admin123",  # Demo password
        restaurant_id="rest_004",
        name="Admin Burger Hub"
    ),
    "user_005": User(
        id="user_005",
        email="admin@tandoorexpress.com",
        password="admin123",  # Demo password
        restaurant_id="rest_005",
        name="Admin Tandoor Express"
    ),
}

