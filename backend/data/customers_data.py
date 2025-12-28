"""
Hardcoded customers data - Acts like customers table
"""
from models.customer import Customer

CUSTOMERS = {
    "1": Customer(
        id="1",
        restaurant_id="rest_001",
        phone="9876543210",
        latitude=19.0760,  # Mumbai coordinates
        longitude=72.8777
    ),
    "2": Customer(
        id="2",
        restaurant_id="rest_002",
        phone="9123456780",
        latitude=28.6139,  # Delhi coordinates
        longitude=77.2090
    ),
    "3": Customer(
        id="3",
        restaurant_id="rest_001",  # Another customer for restaurant 1
        phone="9988776655",
        latitude=19.0759,  # Near Mumbai restaurant
        longitude=72.8776
    ),
    # Additional customers for testing
    "cust_001_new": Customer(
        id="cust_001_new",
        restaurant_id="rest_001",
        phone="9765432109",
        latitude=19.0761,
        longitude=72.8778
    ),
    "cust_002_new": Customer(
        id="cust_002_new",
        restaurant_id="rest_002",
        phone="9234567891",
        latitude=28.6140,
        longitude=77.2091
    ),
    "cust_003_new": Customer(
        id="cust_003_new",
        restaurant_id="rest_002",
        phone="9345678902",
        latitude=28.6141,
        longitude=77.2092
    ),
    "cust_004_new": Customer(
        id="cust_004_new",
        restaurant_id="rest_003",
        phone="9456789013",
        latitude=15.2993,
        longitude=73.9576
    ),
    "cust_005_new": Customer(
        id="cust_005_new",
        restaurant_id="rest_003",
        phone="9567890124",
        latitude=15.2994,
        longitude=73.9577
    ),
    "cust_006_new": Customer(
        id="cust_006_new",
        restaurant_id="rest_003",
        phone="9678901235",
        latitude=15.2995,
        longitude=73.9578
    ),
    "cust_007_new": Customer(
        id="cust_007_new",
        restaurant_id="rest_004",
        phone="9789012346",
        latitude=12.9716,
        longitude=77.5946
    ),
    "cust_008_new": Customer(
        id="cust_008_new",
        restaurant_id="rest_004",
        phone="9890123457",
        latitude=12.9717,
        longitude=77.5947
    ),
    "cust_009_new": Customer(
        id="cust_009_new",
        restaurant_id="rest_004",
        phone="9901234568",
        latitude=12.9718,
        longitude=77.5948
    ),
    "cust_010_new": Customer(
        id="cust_010_new",
        restaurant_id="rest_005",
        phone="9012345679",
        latitude=17.3850,
        longitude=78.4867
    ),
    "cust_011_new": Customer(
        id="cust_011_new",
        restaurant_id="rest_005",
        phone="9123456780",
        latitude=17.3851,
        longitude=78.4868
    ),
    "cust_012_new": Customer(
        id="cust_012_new",
        restaurant_id="rest_005",
        phone="9234567891",
        latitude=17.3852,
        longitude=78.4869
    ),
}

