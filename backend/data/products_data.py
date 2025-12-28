"""
Hardcoded products data - Acts like products table
"""
from models.product import Product

PRODUCTS = {
    # Spice Garden products
    "prod_001": Product(
        id="prod_001",
        restaurant_id="rest_001",
        name="Butter Chicken",
        description="Creamy tomato-based curry with tender chicken",
        price=350.0,
        category="Main Course",
        is_available=True
    ),
    "prod_002": Product(
        id="prod_002",
        restaurant_id="rest_001",
        name="Biryani",
        description="Fragrant basmati rice with spiced meat",
        price=280.0,
        category="Main Course",
        is_available=True
    ),
    "prod_003": Product(
        id="prod_003",
        restaurant_id="rest_001",
        name="Paneer Tikka",
        description="Grilled cottage cheese with spices",
        price=220.0,
        category="Appetizer",
        is_available=True
    ),
    "prod_004": Product(
        id="prod_004",
        restaurant_id="rest_001",
        name="Naan",
        description="Freshly baked leavened bread",
        price=50.0,
        category="Bread",
        is_available=True
    ),
    "prod_005": Product(
        id="prod_005",
        restaurant_id="rest_001",
        name="Dal Makhani",
        description="Creamy black lentils",
        price=180.0,
        category="Main Course",
        is_available=True
    ),
    "prod_006": Product(
        id="prod_006",
        restaurant_id="rest_001",
        name="Gulab Jamun",
        description="Sweet milk dumplings in syrup",
        price=100.0,
        category="Dessert",
        is_available=True
    ),
    
    # Pizza Paradise products
    "prod_007": Product(
        id="prod_007",
        restaurant_id="rest_002",
        name="Margherita Pizza",
        description="Classic tomato, mozzarella, basil",
        price=299.0,
        category="Pizza",
        is_available=True
    ),
    "prod_008": Product(
        id="prod_008",
        restaurant_id="rest_002",
        name="Pepperoni Pizza",
        description="Pepperoni, cheese, tomato sauce",
        price=399.0,
        category="Pizza",
        is_available=True
    ),
    "prod_009": Product(
        id="prod_009",
        restaurant_id="rest_002",
        name="Veg Supreme Pizza",
        description="Mixed vegetables, cheese, sauce",
        price=349.0,
        category="Pizza",
        is_available=True
    ),
    "prod_010": Product(
        id="prod_010",
        restaurant_id="rest_002",
        name="Garlic Bread",
        description="Crispy bread with garlic butter",
        price=99.0,
        category="Side",
        is_available=True
    ),
    "prod_011": Product(
        id="prod_011",
        restaurant_id="rest_002",
        name="Caesar Salad",
        description="Fresh lettuce, croutons, Caesar dressing",
        price=179.0,
        category="Salad",
        is_available=True
    ),
    "prod_012": Product(
        id="prod_012",
        restaurant_id="rest_002",
        name="Chocolate Brownie",
        description="Warm chocolate brownie with ice cream",
        price=149.0,
        category="Dessert",
        is_available=True
    ),
    
    # Sushi Masters (rest_003) products
    "prod_013": Product(
        id="prod_013",
        restaurant_id="rest_003",
        name="Salmon Sashimi",
        description="Fresh Atlantic salmon, sliced thin",
        price=450.0,
        category="Sashimi",
        is_available=True
    ),
    "prod_014": Product(
        id="prod_014",
        restaurant_id="rest_003",
        name="California Roll",
        description="Crab, avocado, cucumber, tobiko",
        price=320.0,
        category="Sushi Roll",
        is_available=True
    ),
    "prod_015": Product(
        id="prod_015",
        restaurant_id="rest_003",
        name="Dragon Roll",
        description="Eel, cucumber, avocado, eel sauce",
        price=480.0,
        category="Sushi Roll",
        is_available=True
    ),
    "prod_016": Product(
        id="prod_016",
        restaurant_id="rest_003",
        name="Miso Soup",
        description="Traditional Japanese soybean soup",
        price=120.0,
        category="Soup",
        is_available=True
    ),
    "prod_017": Product(
        id="prod_017",
        restaurant_id="rest_003",
        name="Tempura Udon",
        description="Wheat noodles in broth with tempura",
        price=380.0,
        category="Noodles",
        is_available=True
    ),
    "prod_018": Product(
        id="prod_018",
        restaurant_id="rest_003",
        name="Green Tea Ice Cream",
        description="Creamy matcha-flavored ice cream",
        price=150.0,
        category="Dessert",
        is_available=True
    ),
    
    # Burger Hub (rest_004) products
    "prod_019": Product(
        id="prod_019",
        restaurant_id="rest_004",
        name="Classic Cheeseburger",
        description="Beef patty, cheese, lettuce, tomato, special sauce",
        price=199.0,
        category="Burger",
        is_available=True
    ),
    "prod_020": Product(
        id="prod_020",
        restaurant_id="rest_004",
        name="BBQ Bacon Burger",
        description="Beef patty, crispy bacon, BBQ sauce, onion rings",
        price=279.0,
        category="Burger",
        is_available=True
    ),
    "prod_021": Product(
        id="prod_021",
        restaurant_id="rest_004",
        name="Veggie Delight",
        description="Plant-based patty, avocado, sprouts, vegan mayo",
        price=229.0,
        category="Burger",
        is_available=True
    ),
    "prod_022": Product(
        id="prod_022",
        restaurant_id="rest_004",
        name="French Fries",
        description="Crispy golden fries, served hot",
        price=99.0,
        category="Side",
        is_available=True
    ),
    "prod_023": Product(
        id="prod_023",
        restaurant_id="rest_004",
        name="Onion Rings",
        description="Beer-battered onion rings",
        price=129.0,
        category="Side",
        is_available=True
    ),
    "prod_024": Product(
        id="prod_024",
        restaurant_id="rest_004",
        name="Chocolate Milkshake",
        description="Rich chocolate milkshake with whipped cream",
        price=149.0,
        category="Beverage",
        is_available=True
    ),
    
    # Tandoor Express (rest_005) products
    "prod_025": Product(
        id="prod_025",
        restaurant_id="rest_005",
        name="Chicken Tikka",
        description="Tender chicken pieces marinated in spices, grilled in tandoor",
        price=320.0,
        category="Tandoor",
        is_available=True
    ),
    "prod_026": Product(
        id="prod_026",
        restaurant_id="rest_005",
        name="Lamb Kebabs",
        description="Juicy minced lamb kebabs, charcoal grilled",
        price=380.0,
        category="Tandoor",
        is_available=True
    ),
    "prod_027": Product(
        id="prod_027",
        restaurant_id="rest_005",
        name="Butter Naan",
        description="Soft bread brushed with butter, baked in tandoor",
        price=60.0,
        category="Bread",
        is_available=True
    ),
    "prod_028": Product(
        id="prod_028",
        restaurant_id="rest_005",
        name="Paneer Makhani",
        description="Cottage cheese in rich tomato butter gravy",
        price=280.0,
        category="Curry",
        is_available=True
    ),
    "prod_029": Product(
        id="prod_029",
        restaurant_id="rest_005",
        name="Dal Tadka",
        description="Spiced lentils tempered with ghee and spices",
        price=180.0,
        category="Curry",
        is_available=True
    ),
    "prod_030": Product(
        id="prod_030",
        restaurant_id="rest_005",
        name="Gulab Jamun",
        description="Sweet milk dumplings in rose-scented sugar syrup",
        price=100.0,
        category="Dessert",
        is_available=True
    ),
}

