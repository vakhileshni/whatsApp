"""
Hardcoded restaurants data - Acts like restaurants table
"""
from models.restaurant import Restaurant

RESTAURANTS = {
    "rest_001": Restaurant(
        id="rest_001",
        name="Spice Garden",
        phone="+919151338489",
        address="123 Main Street, Mumbai",
        latitude=19.0760,
        longitude=72.8777,
        delivery_fee=40.0,
        is_active=True,
        upi_id=""
    ),
    "rest_002": Restaurant(
        id="rest_002",
        name="Pizza Paradise",
        phone="+919876543211",
        address="456 Food Court, Delhi",
        latitude=28.6139,
        longitude=77.2090,
        delivery_fee=40.0,
        is_active=True,
        upi_id=""
    ),
    "rest_003": Restaurant(
        id="rest_003",
        name="Sushi Masters",
        phone="+919876543212",
        address="789 Seaside Boulevard, Goa",
        latitude=15.2993,
        longitude=74.1240,
        delivery_fee=50.0,
        is_active=True,
        upi_id=""
    ),
    "rest_004": Restaurant(
        id="rest_004",
        name="Burger Hub",
        phone="+919876543213",
        address="321 Fast Food Lane, Bangalore",
        latitude=12.9716,
        longitude=77.5946,
        delivery_fee=35.0,
        is_active=True,
        upi_id=""
    ),
    "rest_005": Restaurant(
        id="rest_005",
        name="Tandoor Express",
        phone="+919876543214",
        address="654 Spice Road, Hyderabad",
        latitude=17.3850,
        longitude=78.4867,
        delivery_fee=45.0,
        is_active=True,
        upi_id=""
    ),
}

