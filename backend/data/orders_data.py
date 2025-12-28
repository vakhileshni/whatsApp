"""
Hardcoded orders data - Acts like orders table
"""
from typing import Dict
from models.order import Order, OrderItem
from datetime import datetime, timedelta

# Get current time for realistic timestamps
now = datetime.now()
one_hour_ago = now - timedelta(hours=1)
two_hours_ago = now - timedelta(hours=2)
three_hours_ago = now - timedelta(hours=3)
today_morning = now.replace(hour=10, minute=30)
today_afternoon = now.replace(hour=14, minute=15)

def format_datetime(dt):
    return dt.isoformat()

# Pre-populated orders for testing - Lots of data for all restaurants
ORDERS: Dict[str, Order] = {
    # ===== RESTAURANT 1 (Spice Garden - rest_001) =====
    "order_001": Order(
        id="order_001",
        restaurant_id="rest_001",
        customer_id="1",
        customer_phone="9876543210",
        customer_name="Rajesh Kumar",
        items=[
            OrderItem(product_id="prod_001", product_name="Butter Chicken", quantity=2, price=350.0),
            OrderItem(product_id="prod_004", product_name="Naan", quantity=4, price=50.0),
            OrderItem(product_id="prod_005", product_name="Dal Makhani", quantity=1, price=180.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=1020.0,
        status="pending",
        created_at=format_datetime(now - timedelta(minutes=5)),
        updated_at=format_datetime(now - timedelta(minutes=5)),
        delivery_address="123 MG Road, Andheri East, Mumbai 400069"
    ),
    "order_002": Order(
        id="order_002",
        restaurant_id="rest_001",
        customer_id="3",
        customer_phone="9988776655",
        customer_name="Priya Sharma",
        items=[
            OrderItem(product_id="prod_002", product_name="Biryani", quantity=1, price=280.0),
            OrderItem(product_id="prod_003", product_name="Paneer Tikka", quantity=1, price=220.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=540.0,
        status="preparing",
        created_at=format_datetime(one_hour_ago),
        updated_at=format_datetime(now - timedelta(minutes=20)),
        delivery_address="456 Juhu Beach Road, Juhu, Mumbai 400049"
    ),
    "order_003": Order(
        id="order_003",
        restaurant_id="rest_001",
        customer_id="1",
        customer_phone="9876543210",
        customer_name="Rajesh Kumar",
        items=[
            OrderItem(product_id="prod_001", product_name="Butter Chicken", quantity=1, price=350.0),
            OrderItem(product_id="prod_004", product_name="Naan", quantity=2, price=50.0),
            OrderItem(product_id="prod_006", product_name="Gulab Jamun", quantity=2, price=100.0)
        ],
        order_type="pickup",
        delivery_fee=0.0,
        total_amount=650.0,
        status="ready",
        created_at=format_datetime(two_hours_ago),
        updated_at=format_datetime(now - timedelta(minutes=15)),
    ),
    "order_004": Order(
        id="order_004",
        restaurant_id="rest_001",
        customer_id="1",
        customer_phone="9876543210",
        customer_name="Rajesh Kumar",
        items=[
            OrderItem(product_id="prod_002", product_name="Biryani", quantity=3, price=280.0),
            OrderItem(product_id="prod_005", product_name="Dal Makhani", quantity=2, price=180.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=1300.0,
        status="delivered",
        created_at=format_datetime(three_hours_ago),
        updated_at=format_datetime(one_hour_ago),
        delivery_address="789 Bandra West, Mumbai 400050"
    ),
    "order_005": Order(
        id="order_005",
        restaurant_id="rest_001",
        customer_id="cust_001_new",
        customer_phone="9765432109",
        customer_name="Amit Patel",
        items=[
            OrderItem(product_id="prod_003", product_name="Paneer Tikka", quantity=2, price=220.0),
            OrderItem(product_id="prod_004", product_name="Naan", quantity=3, price=50.0)
        ],
        order_type="pickup",
        delivery_fee=0.0,
        total_amount=590.0,
        status="pending",
        created_at=format_datetime(now - timedelta(minutes=2)),
        updated_at=format_datetime(now - timedelta(minutes=2)),
    ),
    
    # ===== RESTAURANT 2 (Pizza Paradise - rest_002) =====
    "order_006": Order(
        id="order_006",
        restaurant_id="rest_002",
        customer_id="2",
        customer_phone="9123456780",
        customer_name="Sneha Reddy",
        items=[
            OrderItem(product_id="prod_008", product_name="Pepperoni Pizza", quantity=2, price=399.0),
            OrderItem(product_id="prod_010", product_name="Garlic Bread", quantity=1, price=99.0),
            OrderItem(product_id="prod_012", product_name="Chocolate Brownie", quantity=1, price=149.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=986.0,
        status="pending",
        created_at=format_datetime(now - timedelta(minutes=8)),
        updated_at=format_datetime(now - timedelta(minutes=8)),
        delivery_address="321 Connaught Place, New Delhi 110001"
    ),
    "order_007": Order(
        id="order_007",
        restaurant_id="rest_002",
        customer_id="2",
        customer_phone="9123456780",
        customer_name="Sneha Reddy",
        items=[
            OrderItem(product_id="prod_007", product_name="Margherita Pizza", quantity=1, price=299.0),
            OrderItem(product_id="prod_011", product_name="Caesar Salad", quantity=1, price=179.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=518.0,
        status="preparing",
        created_at=format_datetime(one_hour_ago + timedelta(minutes=10)),
        updated_at=format_datetime(now - timedelta(minutes=25)),
        delivery_address="654 Saket, New Delhi 110017"
    ),
    "order_008": Order(
        id="order_008",
        restaurant_id="rest_002",
        customer_id="cust_002_new",
        customer_phone="9234567891",
        customer_name="Vikram Singh",
        items=[
            OrderItem(product_id="prod_009", product_name="Veg Supreme Pizza", quantity=1, price=349.0),
            OrderItem(product_id="prod_010", product_name="Garlic Bread", quantity=2, price=99.0)
        ],
        order_type="pickup",
        delivery_fee=0.0,
        total_amount=547.0,
        status="ready",
        created_at=format_datetime(two_hours_ago + timedelta(minutes=30)),
        updated_at=format_datetime(now - timedelta(minutes=10)),
    ),
    "order_009": Order(
        id="order_009",
        restaurant_id="rest_002",
        customer_id="2",
        customer_phone="9123456780",
        customer_name="Sneha Reddy",
        items=[
            OrderItem(product_id="prod_008", product_name="Pepperoni Pizza", quantity=1, price=399.0),
            OrderItem(product_id="prod_012", product_name="Chocolate Brownie", quantity=2, price=149.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=737.0,
        status="delivered",
        created_at=format_datetime(three_hours_ago + timedelta(minutes=15)),
        updated_at=format_datetime(two_hours_ago),
        delivery_address="987 Dwarka Sector 14, New Delhi 110075"
    ),
    "order_010": Order(
        id="order_010",
        restaurant_id="rest_002",
        customer_id="cust_003_new",
        customer_phone="9345678902",
        customer_name="Anjali Mehta",
        items=[
            OrderItem(product_id="prod_007", product_name="Margherita Pizza", quantity=3, price=299.0),
            OrderItem(product_id="prod_011", product_name="Caesar Salad", quantity=2, price=179.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=1315.0,
        status="preparing",
        created_at=format_datetime(now - timedelta(minutes=30)),
        updated_at=format_datetime(now - timedelta(minutes=12)),
        delivery_address="147 Rohini Sector 18, New Delhi 110089"
    ),
    
    # ===== RESTAURANT 3 (Sushi Masters - rest_003) =====
    "order_011": Order(
        id="order_011",
        restaurant_id="rest_003",
        customer_id="cust_004_new",
        customer_phone="9456789013",
        customer_name="Yuki Tanaka",
        items=[
            OrderItem(product_id="prod_013", product_name="Salmon Sashimi", quantity=2, price=450.0),
            OrderItem(product_id="prod_014", product_name="California Roll", quantity=1, price=320.0),
            OrderItem(product_id="prod_016", product_name="Miso Soup", quantity=2, price=120.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=1380.0,
        status="pending",
        created_at=format_datetime(now - timedelta(minutes=12)),
        updated_at=format_datetime(now - timedelta(minutes=12)),
        delivery_address="258 Calangute Beach Road, Goa 403516"
    ),
    "order_012": Order(
        id="order_012",
        restaurant_id="rest_003",
        customer_id="cust_005_new",
        customer_phone="9567890124",
        customer_name="Rahul Desai",
        items=[
            OrderItem(product_id="prod_015", product_name="Dragon Roll", quantity=1, price=480.0),
            OrderItem(product_id="prod_017", product_name="Tempura Udon", quantity=1, price=380.0)
        ],
        order_type="pickup",
        delivery_fee=0.0,
        total_amount=860.0,
        status="preparing",
        created_at=format_datetime(one_hour_ago + timedelta(minutes=20)),
        updated_at=format_datetime(now - timedelta(minutes=18)),
    ),
    "order_013": Order(
        id="order_013",
        restaurant_id="rest_003",
        customer_id="cust_004_new",
        customer_phone="9456789013",
        customer_name="Yuki Tanaka",
        items=[
            OrderItem(product_id="prod_014", product_name="California Roll", quantity=3, price=320.0),
            OrderItem(product_id="prod_018", product_name="Green Tea Ice Cream", quantity=2, price=150.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=1240.0,
        status="ready",
        created_at=format_datetime(two_hours_ago + timedelta(minutes=45)),
        updated_at=format_datetime(now - timedelta(minutes=8)),
        delivery_address="369 Baga Beach, Goa 403516"
    ),
    "order_014": Order(
        id="order_014",
        restaurant_id="rest_003",
        customer_id="cust_006_new",
        customer_phone="9678901235",
        customer_name="Meera Shah",
        items=[
            OrderItem(product_id="prod_013", product_name="Salmon Sashimi", quantity=1, price=450.0),
            OrderItem(product_id="prod_015", product_name="Dragon Roll", quantity=1, price=480.0),
            OrderItem(product_id="prod_016", product_name="Miso Soup", quantity=1, price=120.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=1090.0,
        status="delivered",
        created_at=format_datetime(three_hours_ago + timedelta(minutes=30)),
        updated_at=format_datetime(one_hour_ago + timedelta(minutes=30)),
        delivery_address="741 Anjuna Beach, Goa 403509"
    ),
    "order_015": Order(
        id="order_015",
        restaurant_id="rest_003",
        customer_id="cust_005_new",
        customer_phone="9567890124",
        customer_name="Rahul Desai",
        items=[
            OrderItem(product_id="prod_017", product_name="Tempura Udon", quantity=2, price=380.0),
            OrderItem(product_id="prod_018", product_name="Green Tea Ice Cream", quantity=1, price=150.0)
        ],
        order_type="pickup",
        delivery_fee=0.0,
        total_amount=910.0,
        status="pending",
        created_at=format_datetime(now - timedelta(minutes=3)),
        updated_at=format_datetime(now - timedelta(minutes=3)),
    ),
    
    # ===== RESTAURANT 4 (Burger Hub - rest_004) =====
    "order_016": Order(
        id="order_016",
        restaurant_id="rest_004",
        customer_id="cust_007_new",
        customer_phone="9789012346",
        customer_name="Arjun Nair",
        items=[
            OrderItem(product_id="prod_019", product_name="Classic Cheeseburger", quantity=2, price=199.0),
            OrderItem(product_id="prod_022", product_name="French Fries", quantity=2, price=99.0),
            OrderItem(product_id="prod_024", product_name="Chocolate Milkshake", quantity=2, price=149.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=834.0,
        status="pending",
        created_at=format_datetime(now - timedelta(minutes=15)),
        updated_at=format_datetime(now - timedelta(minutes=15)),
        delivery_address="852 Indiranagar, Bangalore 560038"
    ),
    "order_017": Order(
        id="order_017",
        restaurant_id="rest_004",
        customer_id="cust_008_new",
        customer_phone="9890123457",
        customer_name="Deepa Iyer",
        items=[
            OrderItem(product_id="prod_020", product_name="BBQ Bacon Burger", quantity=1, price=279.0),
            OrderItem(product_id="prod_023", product_name="Onion Rings", quantity=1, price=129.0)
        ],
        order_type="pickup",
        delivery_fee=0.0,
        total_amount=408.0,
        status="preparing",
        created_at=format_datetime(one_hour_ago + timedelta(minutes=35)),
        updated_at=format_datetime(now - timedelta(minutes=22)),
    ),
    "order_018": Order(
        id="order_018",
        restaurant_id="rest_004",
        customer_id="cust_007_new",
        customer_phone="9789012346",
        customer_name="Arjun Nair",
        items=[
            OrderItem(product_id="prod_021", product_name="Veggie Delight", quantity=2, price=229.0),
            OrderItem(product_id="prod_022", product_name="French Fries", quantity=3, price=99.0),
            OrderItem(product_id="prod_024", product_name="Chocolate Milkshake", quantity=1, price=149.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=995.0,
        status="ready",
        created_at=format_datetime(two_hours_ago + timedelta(minutes=20)),
        updated_at=format_datetime(now - timedelta(minutes=5)),
        delivery_address="963 Koramangala 5th Block, Bangalore 560095"
    ),
    "order_019": Order(
        id="order_019",
        restaurant_id="rest_004",
        customer_id="cust_009_new",
        customer_phone="9901234568",
        customer_name="Kiran Rao",
        items=[
            OrderItem(product_id="prod_019", product_name="Classic Cheeseburger", quantity=4, price=199.0),
            OrderItem(product_id="prod_022", product_name="French Fries", quantity=4, price=99.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=1196.0,
        status="delivered",
        created_at=format_datetime(three_hours_ago + timedelta(minutes=10)),
        updated_at=format_datetime(two_hours_ago + timedelta(minutes=15)),
        delivery_address="147 Whitefield Main Road, Bangalore 560066"
    ),
    "order_020": Order(
        id="order_020",
        restaurant_id="rest_004",
        customer_id="cust_008_new",
        customer_phone="9890123457",
        customer_name="Deepa Iyer",
        items=[
            OrderItem(product_id="prod_020", product_name="BBQ Bacon Burger", quantity=2, price=279.0),
            OrderItem(product_id="prod_023", product_name="Onion Rings", quantity=2, price=129.0),
            OrderItem(product_id="prod_024", product_name="Chocolate Milkshake", quantity=2, price=149.0)
        ],
        order_type="pickup",
        delivery_fee=0.0,
        total_amount=1114.0,
        status="preparing",
        created_at=format_datetime(now - timedelta(minutes=25)),
        updated_at=format_datetime(now - timedelta(minutes=14)),
    ),
    
    # ===== RESTAURANT 5 (Tandoor Express - rest_005) =====
    "order_021": Order(
        id="order_021",
        restaurant_id="rest_005",
        customer_id="cust_010_new",
        customer_phone="9012345679",
        customer_name="Ravi Verma",
        items=[
            OrderItem(product_id="prod_025", product_name="Chicken Tikka", quantity=2, price=320.0),
            OrderItem(product_id="prod_027", product_name="Butter Naan", quantity=4, price=60.0),
            OrderItem(product_id="prod_029", product_name="Dal Tadka", quantity=1, price=180.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=1100.0,
        status="pending",
        created_at=format_datetime(now - timedelta(minutes=18)),
        updated_at=format_datetime(now - timedelta(minutes=18)),
        delivery_address="258 Banjara Hills, Hyderabad 500034"
    ),
    "order_022": Order(
        id="order_022",
        restaurant_id="rest_005",
        customer_id="cust_011_new",
        customer_phone="9123456780",
        customer_name="Lakshmi Menon",
        items=[
            OrderItem(product_id="prod_026", product_name="Lamb Kebabs", quantity=1, price=380.0),
            OrderItem(product_id="prod_028", product_name="Paneer Makhani", quantity=1, price=280.0),
            OrderItem(product_id="prod_027", product_name="Butter Naan", quantity=2, price=60.0)
        ],
        order_type="pickup",
        delivery_fee=0.0,
        total_amount=780.0,
        status="preparing",
        created_at=format_datetime(one_hour_ago + timedelta(minutes=5)),
        updated_at=format_datetime(now - timedelta(minutes=28)),
    ),
    "order_023": Order(
        id="order_023",
        restaurant_id="rest_005",
        customer_id="cust_010_new",
        customer_phone="9012345679",
        customer_name="Ravi Verma",
        items=[
            OrderItem(product_id="prod_025", product_name="Chicken Tikka", quantity=1, price=320.0),
            OrderItem(product_id="prod_027", product_name="Butter Naan", quantity=3, price=60.0),
            OrderItem(product_id="prod_030", product_name="Gulab Jamun", quantity=2, price=100.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=620.0,
        status="ready",
        created_at=format_datetime(two_hours_ago + timedelta(minutes=10)),
        updated_at=format_datetime(now - timedelta(minutes=6)),
        delivery_address="369 Jubilee Hills, Hyderabad 500033"
    ),
    "order_024": Order(
        id="order_024",
        restaurant_id="rest_005",
        customer_id="cust_012_new",
        customer_phone="9234567891",
        customer_name="Suresh Pillai",
        items=[
            OrderItem(product_id="prod_026", product_name="Lamb Kebabs", quantity=2, price=380.0),
            OrderItem(product_id="prod_028", product_name="Paneer Makhani", quantity=2, price=280.0),
            OrderItem(product_id="prod_029", product_name="Dal Tadka", quantity=1, price=180.0)
        ],
        order_type="delivery",
        delivery_fee=40.0,
        total_amount=1660.0,
        status="delivered",
        created_at=format_datetime(three_hours_ago + timedelta(minutes=40)),
        updated_at=format_datetime(one_hour_ago + timedelta(minutes=45)),
        delivery_address="741 Hitech City, Hyderabad 500081"
    ),
    "order_025": Order(
        id="order_025",
        restaurant_id="rest_005",
        customer_id="cust_011_new",
        customer_phone="9123456780",
        customer_name="Lakshmi Menon",
        items=[
            OrderItem(product_id="prod_025", product_name="Chicken Tikka", quantity=3, price=320.0),
            OrderItem(product_id="prod_027", product_name="Butter Naan", quantity=6, price=60.0)
        ],
        order_type="pickup",
        delivery_fee=0.0,
        total_amount=1320.0,
        status="pending",
        created_at=format_datetime(now - timedelta(minutes=1)),
        updated_at=format_datetime(now - timedelta(minutes=1)),
    ),
}
