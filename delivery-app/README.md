# Delivery Person Android App

This is a separate Android app for delivery persons to:
- Show their availability status
- Track and share their live location
- Receive delivery order notifications
- Accept and complete delivery orders

## Features

1. **Availability Management**
   - Toggle availability on/off
   - View current availability status

2. **Live Location Tracking**
   - Share real-time location with the system
   - View current location on map
   - Automatic location updates

3. **Order Management**
   - View available delivery orders
   - Accept delivery orders
   - Navigate to restaurant and customer locations
   - Mark orders as delivered

4. **Authentication**
   - Sign up as delivery person
   - Login/Logout
   - Profile management

## Setup

1. Update `app/build.gradle.kts` with your backend API URL
2. Build and run the app
3. Sign up or login as a delivery person
4. Enable location permissions
5. Toggle availability to start receiving orders

## Backend Integration

The app connects to:
- `/api/v1/delivery/signup` - Register delivery person
- `/api/v1/delivery/login` - Login
- `/api/v1/delivery/availability` - Update availability
- `/api/v1/delivery/location` - Update location
- `/api/v1/delivery/orders` - Get available orders
- `/api/v1/delivery/orders/{order_id}/accept` - Accept order
- `/api/v1/delivery/orders/{order_id}/complete` - Complete delivery
