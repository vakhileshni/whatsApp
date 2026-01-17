package com.deliveryperson.ui.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.deliveryperson.data.repository.DeliveryRepository
import com.deliveryperson.network.LoginResponse
import com.deliveryperson.network.SignUpRequest
import com.deliveryperson.network.SignUpResponse
import com.deliveryperson.network.RetrofitClient
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class AuthUiState {
    object Idle : AuthUiState()
    object Loading : AuthUiState()
    data class Success(val loginResponse: LoginResponse) : AuthUiState()
    data class SignUpSuccess(val signUpResponse: SignUpResponse) : AuthUiState()
    data class Error(val message: String) : AuthUiState()
}

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val deliveryRepository: DeliveryRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow<AuthUiState>(AuthUiState.Idle)
    val uiState: StateFlow<AuthUiState> = _uiState.asStateFlow()

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _uiState.value = AuthUiState.Loading
            deliveryRepository.login(email, password)
                .onSuccess { response ->
                    // Store token
                    RetrofitClient.setAuthToken(response.access_token)
                    _uiState.value = AuthUiState.Success(response)
                }
                .onFailure { error ->
                    _uiState.value = AuthUiState.Error(error.message ?: "Login failed")
                }
        }
    }

    fun signup(
        name: String,
        phone: String,
        email: String,
        password: String,
        vehicleType: String,
        licenseNumber: String?
    ) {
        viewModelScope.launch {
            _uiState.value = AuthUiState.Loading
            val request = SignUpRequest(
                name = name,
                phone = phone,
                email = email,
                password = password,
                vehicle_type = vehicleType,
                license_number = licenseNumber
            )
            deliveryRepository.signup(request)
                .onSuccess { response ->
                    _uiState.value = AuthUiState.SignUpSuccess(response)
                }
                .onFailure { error ->
                    _uiState.value = AuthUiState.Error(error.message ?: "Signup failed")
                }
        }
    }

    fun logout() {
        RetrofitClient.setAuthToken(null)
        _uiState.value = AuthUiState.Idle
    }
}
