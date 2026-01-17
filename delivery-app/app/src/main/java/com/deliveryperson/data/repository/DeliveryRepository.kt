package com.deliveryperson.data.repository

import com.deliveryperson.network.ApiService
import com.deliveryperson.network.*
import javax.inject.Inject

class DeliveryRepository @Inject constructor(
    private val apiService: ApiService
) {
    suspend fun login(email: String, password: String): Result<LoginResponse> {
        return try {
            val response = apiService.login(LoginRequest(email, password))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.message() ?: "Login failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun signup(request: SignUpRequest): Result<SignUpResponse> {
        return try {
            val response = apiService.signup(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.message() ?: "Signup failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getDeliveryPersonInfo(): Result<DeliveryPersonResponse> {
        return try {
            val response = apiService.getDeliveryPersonInfo()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.message() ?: "Failed to get info"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateAvailability(request: UpdateAvailabilityRequest): Result<DeliveryPersonResponse> {
        return try {
            val response = apiService.updateAvailability(request)
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.message() ?: "Failed to update availability"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun updateLocation(request: UpdateLocationRequest): Result<String> {
        return try {
            val response = apiService.updateLocation(request)
            if (response.isSuccessful) {
                Result.success("Location updated")
            } else {
                Result.failure(Exception(response.message() ?: "Failed to update location"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun getDeliveryOrders(): Result<List<DeliveryOrder>> {
        return try {
            val response = apiService.getDeliveryOrders()
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                Result.failure(Exception(response.message() ?: "Failed to get orders"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun acceptOrder(orderId: String): Result<String> {
        return try {
            val response = apiService.acceptOrder(orderId)
            if (response.isSuccessful) {
                Result.success("Order accepted")
            } else {
                Result.failure(Exception(response.message() ?: "Failed to accept order"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun completeOrder(orderId: String): Result<String> {
        return try {
            val response = apiService.completeOrder(orderId)
            if (response.isSuccessful) {
                Result.success("Order completed")
            } else {
                Result.failure(Exception(response.message() ?: "Failed to complete order"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
