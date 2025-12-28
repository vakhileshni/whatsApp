"""
Restaurant Registry - Hardcoded restaurant data with menu items
QR codes contain ONLY restaurant_id (e.g., "rest_001")
"""
RESTAURANTS = {
    "rest_001": {
        "id": "rest_001",
        "name": "Spice Garden",
        "upi_id": "spicegarden@upi",
        "menu": [
            {"id": "1", "name": "Butter Chicken", "price": 350},
            {"id": "2", "name": "Biryani", "price": 280},
            {"id": "3", "name": "Paneer Tikka", "price": 220},
            {"id": "4", "name": "Naan", "price": 50},
            {"id": "5", "name": "Dal Makhani", "price": 180},
            {"id": "6", "name": "Gulab Jamun", "price": 100}
        ]
    },
    "rest_002": {
        "id": "rest_002",
        "name": "Pizza Paradise",
        "upi_id": "pizzaparadise@upi",
        "menu": [
            {"id": "1", "name": "Margherita Pizza", "price": 299},
            {"id": "2", "name": "Pepperoni Pizza", "price": 399},
            {"id": "3", "name": "Veg Supreme Pizza", "price": 349},
            {"id": "4", "name": "Garlic Bread", "price": 99},
            {"id": "5", "name": "Caesar Salad", "price": 179},
            {"id": "6", "name": "Chocolate Brownie", "price": 149}
        ]
    },
    "rest_003": {
        "id": "rest_003",
        "name": "Sushi Masters",
        "upi_id": "sushimasters@upi",
        "menu": [
            {"id": "1", "name": "Salmon Sashimi", "price": 450},
            {"id": "2", "name": "California Roll", "price": 320},
            {"id": "3", "name": "Dragon Roll", "price": 480},
            {"id": "4", "name": "Miso Soup", "price": 120},
            {"id": "5", "name": "Tempura Udon", "price": 380},
            {"id": "6", "name": "Green Tea Ice Cream", "price": 150}
        ]
    },
    "rest_004": {
        "id": "rest_004",
        "name": "Burger Hub",
        "upi_id": "burgerhub@upi",
        "menu": [
            {"id": "1", "name": "Classic Cheeseburger", "price": 199},
            {"id": "2", "name": "BBQ Bacon Burger", "price": 279},
            {"id": "3", "name": "Veggie Delight", "price": 229},
            {"id": "4", "name": "French Fries", "price": 99},
            {"id": "5", "name": "Onion Rings", "price": 129},
            {"id": "6", "name": "Chocolate Milkshake", "price": 149}
        ]
    },
    "rest_005": {
        "id": "rest_005",
        "name": "Tandoor Express",
        "upi_id": "tandoorexpress@upi",
        "menu": [
            {"id": "1", "name": "Chicken Tikka", "price": 320},
            {"id": "2", "name": "Lamb Kebabs", "price": 380},
            {"id": "3", "name": "Butter Naan", "price": 60},
            {"id": "4", "name": "Paneer Makhani", "price": 280},
            {"id": "5", "name": "Dal Tadka", "price": 180},
            {"id": "6", "name": "Gulab Jamun", "price": 100}
        ]
    }
}

def get_restaurant_by_id(restaurant_id: str):
    """Get restaurant by ID from registry"""
    return RESTAURANTS.get(restaurant_id)

def get_all_restaurant_ids():
    """Get all restaurant IDs"""
    return list(RESTAURANTS.keys())

def is_valid_restaurant_id(restaurant_id: str) -> bool:
    """Check if restaurant_id exists in registry"""
    return restaurant_id in RESTAURANTS





