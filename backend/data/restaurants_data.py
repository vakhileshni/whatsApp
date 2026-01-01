"""
Hardcoded restaurants data - Acts like restaurants table
"""
from models.restaurant import Restaurant

RESTAURANTS = {
    "rest_001": Restaurant(
        id="rest_001",
        name="Spice Garden",
        phone="+919151338489",
        address="Asiyana, Lucknow",
        latitude=26.8527,
        longitude=80.9495,
        delivery_fee=40.0,
        is_active=True,
        upi_id="spicegarden@upi",
        cuisine_type="full-meal"  # Full meal restaurant (veg + non-veg)
    ),
    "rest_002": Restaurant(
        id="rest_002",
        name="Pizza Paradise",
        phone="+919876543211",
        address="Sriganganagar, Lucknow",
        latitude=26.8487,
        longitude=80.9468,
        delivery_fee=40.0,
        is_active=True,
        upi_id="pizzaparadise@upi",
        cuisine_type="both"  # Both veg and non-veg
    ),
    "rest_003": Restaurant(
        id="rest_003",
        name="Sushi Masters",
        phone="+919876543212",
        address="Alambagh, Lucknow",
        latitude=26.8408,
        longitude=80.9433,
        delivery_fee=50.0,
        is_active=True,
        upi_id="sushimasters@upi",
        cuisine_type="non-veg"  # Non-veg focused
    ),
    "rest_004": Restaurant(
        id="rest_004",
        name="Burger Hub",
        phone="+919876543213",
        address="Asiyana Road, Lucknow",
        latitude=26.8565,
        longitude=80.9521,
        delivery_fee=35.0,
        is_active=True,
        upi_id="burgerhub@upi",
        cuisine_type="snack"  # Snacks/Fast food
    ),
    "rest_005": Restaurant(
        id="rest_005",
        name="Tandoor Express",
        phone="+919876543214",
        address="Alambagh Market, Lucknow",
        latitude=26.8385,
        longitude=80.9415,
        delivery_fee=45.0,
        is_active=True,
        upi_id="tandoorexpress@upi",
        cuisine_type="full-meal"  # Full meal restaurant (veg + non-veg)
    ),
}

