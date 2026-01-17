package com.deliveryperson.network

import com.deliveryperson.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {
    // Auth
    @POST("/api/v1/delivery/login")
    suspend fun login(@Body request: LoginRequest): Response<LoginResponse>

    @POST("/api/v1/delivery/signup")
    suspend fun signup(@Body request: SignUpRequest): Response<SignUpResponse>

    // Delivery Person Info
    @GET("/api/v1/delivery/me")
    suspend fun getDeliveryPersonInfo(): Response<DeliveryPersonResponse>

    // Availability
    @PATCH("/api/v1/delivery/availability")
    suspend fun updateAvailability(@Body request: UpdateAvailabilityRequest): Response<DeliveryPersonResponse>

    // Location
    @POST("/api/v1/delivery/location")
    suspend fun updateLocation(@Body request: UpdateLocationRequest): Response<Map<String, String>>

    // Orders
    @GET("/api/v1/delivery/orders")
    suspend fun getDeliveryOrders(): Response<List<DeliveryOrder>>

    @POST("/api/v1/delivery/orders/{orderId}/accept")
    suspend fun acceptOrder(@Path("orderId") orderId: String): Response<Map<String, String>>

    @POST("/api/v1/delivery/orders/{orderId}/complete")
    suspend fun completeOrder(@Path("orderId") orderId: String): Response<Map<String, String>>
}

data class LoginRequest(
    val email: String,
    val password: String
)

data class LoginResponse(
    val access_token: String,
    val token_type: String = "bearer",
    val delivery_person_id: String,
    val name: String
)

data class SignUpRequest(
    val name: String,
    val phone: String,
    val email: String,
    val password: String,
    val vehicle_type: String = "bike",
    val license_number: String? = null
)

data class SignUpResponse(
    val message: String,
    val delivery_person_id: String
)

data class DeliveryPersonResponse(
    val id: String,
    val name: String,
    val phone: String,
    val email: String,
    val vehicle_type: String,
    val is_available: Boolean,
    val current_latitude: Double?,
    val current_longitude: Double?,
    val created_at: String
)

data class UpdateAvailabilityRequest(
    val is_available: Boolean
)

data class UpdateLocationRequest(
    val latitude: Double,
    val longitude: Double
)

data class DeliveryOrder(
    val order_id: String,
    val restaurant_id: String,
    val restaurant_name: String,
    val restaurant_address: String,
    val customer_name: String,
    val customer_phone: String,
    val delivery_address: String,
    val customer_latitude: Double?,
    val customer_longitude: Double?,
    val total_amount: Double,
    val order_items: List<OrderItem>,
    val created_at: String,
    val status: String
)

data class OrderItem(
    val product_name: String,
    val quantity: Int,
    val price: Double
)
