package com.deliveryperson.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.deliveryperson.data.repository.DeliveryRepository
import com.deliveryperson.network.DeliveryPersonResponse
import com.deliveryperson.network.DeliveryOrder
import com.deliveryperson.network.UpdateAvailabilityRequest
import com.deliveryperson.network.UpdateLocationRequest
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class DeliveryPersonUiState {
    object Idle : DeliveryPersonUiState()
    object Loading : DeliveryPersonUiState()
    data class Success(val person: DeliveryPersonResponse) : DeliveryPersonUiState()
    data class Error(val message: String) : DeliveryPersonUiState()
}

sealed class OrdersUiState {
    object Idle : OrdersUiState()
    object Loading : OrdersUiState()
    data class Success(val orders: List<DeliveryOrder>) : OrdersUiState()
    data class Error(val message: String) : OrdersUiState()
}

@HiltViewModel
class DeliveryViewModel @Inject constructor(
    private val deliveryRepository: DeliveryRepository
) : ViewModel() {

    private val _deliveryPersonState = MutableStateFlow<DeliveryPersonUiState>(DeliveryPersonUiState.Idle)
    val deliveryPersonState: StateFlow<DeliveryPersonUiState> = _deliveryPersonState.asStateFlow()

    private val _ordersState = MutableStateFlow<OrdersUiState>(OrdersUiState.Idle)
    val ordersState: StateFlow<OrdersUiState> = _ordersState.asStateFlow()

    fun loadDeliveryPersonInfo() {
        viewModelScope.launch {
            _deliveryPersonState.value = DeliveryPersonUiState.Loading
            deliveryRepository.getDeliveryPersonInfo()
                .onSuccess { person ->
                    _deliveryPersonState.value = DeliveryPersonUiState.Success(person)
                }
                .onFailure { error ->
                    _deliveryPersonState.value = DeliveryPersonUiState.Error(error.message ?: "Failed to load info")
                }
        }
    }

    fun updateAvailability(isAvailable: Boolean) {
        viewModelScope.launch {
            deliveryRepository.updateAvailability(UpdateAvailabilityRequest(isAvailable))
                .onSuccess {
                    loadDeliveryPersonInfo()
                }
                .onFailure { error ->
                    // Handle error
                }
        }
    }

    fun updateLocation(latitude: Double, longitude: Double) {
        viewModelScope.launch {
            deliveryRepository.updateLocation(UpdateLocationRequest(latitude, longitude))
                .onSuccess {
                    // Location updated
                }
                .onFailure { error ->
                    // Handle error
                }
        }
    }

    fun loadOrders() {
        viewModelScope.launch {
            _ordersState.value = OrdersUiState.Loading
            deliveryRepository.getDeliveryOrders()
                .onSuccess { orders ->
                    _ordersState.value = OrdersUiState.Success(orders)
                }
                .onFailure { error ->
                    _ordersState.value = OrdersUiState.Error(error.message ?: "Failed to load orders")
                }
        }
    }

    fun acceptOrder(orderId: String) {
        viewModelScope.launch {
            deliveryRepository.acceptOrder(orderId)
                .onSuccess {
                    loadOrders() // Refresh orders
                }
                .onFailure { error ->
                    // Handle error
                }
        }
    }

    fun completeOrder(orderId: String) {
        viewModelScope.launch {
            deliveryRepository.completeOrder(orderId)
                .onSuccess {
                    loadOrders() // Refresh orders
                }
                .onFailure { error ->
                    // Handle error
                }
        }
    }
}
