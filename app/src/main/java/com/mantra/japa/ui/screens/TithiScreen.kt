package com.mantra.japa.ui.screens

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import com.mantra.japa.R
import com.mantra.japa.TithiReminderScheduler
import com.mantra.japa.ui.theme.SoothingBlue
import com.mantra.japa.ui.viewmodel.MainViewModel
import java.util.TimeZone

@Composable
fun TithiScreen(
    viewModel: MainViewModel
) {
    val panchangResponse by viewModel.panchangResponse.collectAsState()
    val error by viewModel.error.collectAsState()
    val context = LocalContext.current
    val sharedPreferences = context.getSharedPreferences("tithi_prefs", Context.MODE_PRIVATE)

    var lat by remember { mutableStateOf(sharedPreferences.getString("lat", "19.0760") ?: "19.0760") }
    var lon by remember { mutableStateOf(sharedPreferences.getString("lon", "72.8777") ?: "72.8777") }
    var tzone by remember { mutableStateOf(sharedPreferences.getString("tzone", TimeZone.getDefault().id) ?: TimeZone.getDefault().id) }
    var latError by remember { mutableStateOf<String?>(null) }
    var lonError by remember { mutableStateOf<String?>(null) }

    val launcher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            TithiReminderScheduler.scheduleDailyReminder(context)
        } else {
            // Handle permission denial
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(text = stringResource(id = R.string.tithi), style = MaterialTheme.typography.headlineMedium)

        TextField(
            value = lat,
            onValueChange = { lat = it },
            label = { Text(stringResource(id = R.string.latitude)) },
            isError = latError != null,
            modifier = Modifier.fillMaxWidth()
        )
        latError?.let {
            Text(text = it, color = MaterialTheme.colorScheme.error)
        }
        TextField(
            value = lon,
            onValueChange = { lon = it },
            label = { Text(stringResource(id = R.string.longitude)) },
            isError = lonError != null,
            modifier = Modifier.fillMaxWidth()
        )
        lonError?.let {
            Text(text = it, color = MaterialTheme.colorScheme.error)
        }
        TextField(
            value = tzone,
            onValueChange = { tzone = it },
            label = { Text(stringResource(id = R.string.timezone)) },
            modifier = Modifier.fillMaxWidth()
        )

        Button(
            onClick = {
                try {
                    val latDouble = lat.toDouble()
                    latError = null
                    try {
                        val lonDouble = lon.toDouble()
                        lonError = null
                        with(sharedPreferences.edit()) {
                            putString("lat", lat)
                            putString("lon", lon)
                            putString("tzone", tzone)
                            apply()
                        }
                        viewModel.fetchPanchang(latDouble, lonDouble, tzone)
                    } catch (e: NumberFormatException) {
                        lonError = context.getString(R.string.please_enter_a_valid_number)
                    }
                } catch (e: NumberFormatException) {
                    latError = context.getString(R.string.please_enter_a_valid_number)
                }
            },
            modifier = Modifier.padding(vertical = 16.dp)
        ) {
            Text(text = stringResource(id = R.string.fetch_tithi))
        }

        error?.let {
            Text(text = it, color = MaterialTheme.colorScheme.error)
        }

        panchangResponse?.let {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                colors = CardDefaults.cardColors(containerColor = SoothingBlue)
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(text = stringResource(id = R.string.tithi) + ": ${it.tithi.details.tithi_name}", style = MaterialTheme.typography.titleLarge)
                    Text(text = "End Time: ${it.tithi.end_time}", style = MaterialTheme.typography.bodyLarge)
                }
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            Button(onClick = {
                if (ContextCompat.checkSelfPermission(
                        context,
                        Manifest.permission.POST_NOTIFICATIONS
                    ) == PackageManager.PERMISSION_GRANTED
                ) {
                    TithiReminderScheduler.scheduleDailyReminder(context)
                } else {
                    launcher.launch(Manifest.permission.POST_NOTIFICATIONS)
                }
            }) {
                Text(text = stringResource(id = R.string.schedule_reminder))
            }
            Button(onClick = { TithiReminderScheduler.cancelReminder(context) }) {
                Text(text = stringResource(id = R.string.cancel_reminder))
            }
        }
    }
}
