package com.deliveryperson.ui.screen

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.NavController
import com.deliveryperson.ui.viewmodel.DeliveryViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    navController: NavController,
    viewModel: DeliveryViewModel = hiltViewModel()
) {
    val personState by viewModel.deliveryPersonState.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.loadDeliveryPersonInfo()
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Profile") },
                navigationIcon = {
                    IconButton(onClick = { navController.popBackStack() }) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { padding ->
        when (val state = personState) {
            is com.deliveryperson.ui.viewmodel.DeliveryPersonUiState.Idle -> {
                // Initial state
            }
            is com.deliveryperson.ui.viewmodel.DeliveryPersonUiState.Loading -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
            is com.deliveryperson.ui.viewmodel.DeliveryPersonUiState.Success -> {
                Column(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding)
                        .padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(16.dp)
                ) {
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Column(
                            modifier = Modifier.padding(16.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            Text(
                                state.person.name,
                                style = MaterialTheme.typography.headlineMedium
                            )
                            Text("Email: ${state.person.email}")
                            Text("Phone: ${state.person.phone}")
                            Text("Vehicle: ${state.person.vehicle_type}")
                            Text(
                                "Status: ${if (state.person.is_available) "Available" else "Not Available"}"
                            )
                        }
                    }
                }
            }
            is com.deliveryperson.ui.viewmodel.DeliveryPersonUiState.Error -> {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .padding(padding),
                    contentAlignment = Alignment.Center
                ) {
                    Text(state.message)
                }
            }
        }
    }
}
