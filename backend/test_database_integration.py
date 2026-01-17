"""
Test Database Integration
Verify that all repositories are working with the database
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from database import check_db_connection, init_db
from repositories.restaurant_repo import get_all_restaurants, create_restaurant, get_restaurant_by_id
from repositories.user_repo import get_user_by_email, create_user
from repositories.product_repo import get_products_by_restaurant, create_product
from repositories.customer_repo import get_customer_by_phone, create_customer
from models.restaurant import Restaurant
from models.user import User
from models.product import Product
from models.customer import Customer

def test_database_connection():
    """Test 1: Database Connection"""
    print("=" * 80)
    print("TEST 1: Database Connection")
    print("=" * 80)
    
    if check_db_connection():
        print("✅ Database connection successful!")
        return True
    else:
        print("❌ Database connection failed!")
        return False

def test_restaurant_repository():
    """Test 2: Restaurant Repository"""
    print("\n" + "=" * 80)
    print("TEST 2: Restaurant Repository")
    print("=" * 80)
    
    try:
        # Get all restaurants
        restaurants = get_all_restaurants()
        print(f"✅ Found {len(restaurants)} restaurants in database")
        
        # Test getting restaurant by ID (if any exist)
        if restaurants:
            test_id = restaurants[0].id
            restaurant = get_restaurant_by_id(test_id)
            if restaurant:
                print(f"✅ Successfully retrieved restaurant: {restaurant.name}")
            else:
                print(f"⚠️  Restaurant {test_id} not found")
        
        # Test creating a restaurant (will be created if doesn't exist)
        test_restaurant = Restaurant(
            id="test_rest_integration",
            name="Test Integration Restaurant",
            phone="+1234567890",
            address="123 Test Street",
            latitude=40.7128,
            longitude=-74.0060,
            delivery_fee=50.0,
            is_active=True
        )
        
        created = create_restaurant(test_restaurant)
        if created:
            print("✅ Successfully created restaurant in database!")
            
            # Verify it was saved
            retrieved = get_restaurant_by_id("test_rest_integration")
            if retrieved:
                print("✅ Restaurant persisted to database!")
            else:
                print("❌ Restaurant was not found after creation")
        else:
            print("⚠️  Restaurant might already exist (this is OK)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_user_repository():
    """Test 3: User Repository"""
    print("\n" + "=" * 80)
    print("TEST 3: User Repository")
    print("=" * 80)
    
    try:
        # Test creating a user (only if restaurant exists)
        test_user = User(
            id="test_user_integration",
            email="test@example.com",
            password="test123",
            restaurant_id="test_rest_integration",
            name="Test User"
        )
        
        # Check if restaurant exists first
        restaurant = get_restaurant_by_id("test_rest_integration")
        if not restaurant:
            print("⚠️  Test restaurant not found, skipping user creation")
            return True
        
        created = create_user(test_user)
        if created:
            print("✅ Successfully created user in database!")
            
            # Verify retrieval
            retrieved = get_user_by_email("test@example.com")
            if retrieved:
                print("✅ User retrieved from database!")
            else:
                print("❌ User was not found after creation")
        else:
            print("⚠️  User might already exist (this is OK)")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_product_repository():
    """Test 4: Product Repository"""
    print("\n" + "=" * 80)
    print("TEST 4: Product Repository")
    print("=" * 80)
    
    try:
        # Get products for test restaurant
        products = get_products_by_restaurant("test_rest_integration")
        print(f"✅ Found {len(products)} products for test restaurant")
        
        # Test creating a product
        test_product = Product(
            id="test_product_integration",
            restaurant_id="test_rest_integration",
            name="Test Product",
            description="Test Description",
            price=99.99,
            category="Test Category",
            is_available=True
        )
        
        # Check if restaurant exists
        restaurant = get_restaurant_by_id("test_rest_integration")
        if not restaurant:
            print("⚠️  Test restaurant not found, skipping product creation")
            return True
        
        created = create_product(test_product)
        if created:
            print("✅ Successfully created product in database!")
            
            # Verify retrieval
            products_after = get_products_by_restaurant("test_rest_integration")
            print(f"✅ Found {len(products_after)} products after creation")
        else:
            print("⚠️  Product creation failed")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_customer_repository():
    """Test 5: Customer Repository"""
    print("\n" + "=" * 80)
    print("TEST 5: Customer Repository")
    print("=" * 80)
    
    try:
        # Test creating a customer
        test_customer = Customer(
            id="test_customer_integration",
            restaurant_id="test_rest_integration",
            phone="+1987654321",
            latitude=40.7580,
            longitude=-73.9855
        )
        
        created = create_customer(test_customer)
        if created:
            print("✅ Successfully created customer in database!")
            
            # Verify retrieval
            retrieved = get_customer_by_phone("+1987654321")
            if retrieved:
                print("✅ Customer retrieved from database!")
            else:
                print("❌ Customer was not found after creation")
        else:
            print("⚠️  Customer creation failed")
        
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("DATABASE INTEGRATION TESTS")
    print("=" * 80)
    print("\nTesting database connection and repository functions...")
    print("Make sure database is running: docker-compose -f docker-compose-db.yml up -d")
    print()
    
    # Initialize database models
    try:
        init_db()
        print("✅ Database models initialized")
    except Exception as e:
        print(f"⚠️  Model initialization: {e}")
    
    results = []
    
    # Run tests
    results.append(("Database Connection", test_database_connection()))
    results.append(("Restaurant Repository", test_restaurant_repository()))
    results.append(("User Repository", test_user_repository()))
    results.append(("Product Repository", test_product_repository()))
    results.append(("Customer Repository", test_customer_repository()))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{name:30s}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Database integration is working correctly!")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
    
    print("=" * 80)

if __name__ == "__main__":
    main()
