package com.deliveryperson.data.model

data class DeliveryPerson(
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
