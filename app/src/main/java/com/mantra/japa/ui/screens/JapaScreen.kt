package com.mantra.japa.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DatePicker
import androidx.compose.material3.DatePickerDialog
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.material3.rememberDatePickerState
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
import com.mantra.japa.R
import com.mantra.japa.ui.theme.GentlePurple
import com.mantra.japa.ui.viewmodel.MainViewModel
import com.mantra.japa.utils.formatDate
import java.util.Date

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun JapaScreen(
    viewModel: MainViewModel,
    mantraId: Long
) {
    var malas by remember { mutableStateOf(0) }
    val target by viewModel.getTargetForMantra(mantraId).collectAsState()
    var showDialog by remember { mutableStateOf(false) }
    val datePickerState = rememberDatePickerState()
    var targetMalas by remember { mutableStateOf("") }
    var targetMalasError by remember { mutableStateOf<String?>(null) }
    val context = LocalContext.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = stringResource(id = R.string.japa_counter), style = MaterialTheme.typography.headlineMedium)

        Card(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 16.dp),
            elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
            colors = CardDefaults.cardColors(containerColor = GentlePurple)
        ) {
            Column(
                modifier = Modifier.padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Text(text = stringResource(id = R.string.malas, malas), style = MaterialTheme.typography.headlineLarge)
                target?.let {
                    Text(text = stringResource(id = R.string.target, it.targetMalas, formatDate(it.targetDate)), style = MaterialTheme.typography.bodyLarge)
                }
            }
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            Button(onClick = { malas++ }) {
                Text(text = stringResource(id = R.string.increment))
            }
            Button(onClick = {
                viewModel.addJapaEntry(mantraId, malas)
                malas = 0
            }) {
                Text(text = stringResource(id = R.string.save))
            }
        }

        Button(
            onClick = { showDialog = true },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text(text = stringResource(id = R.string.set_target))
        }

        if (showDialog) {
            DatePickerDialog(
                onDismissRequest = { showDialog = false },
                confirmButton = {
                    Button(onClick = {
                        try {
                            val malasInt = targetMalas.toInt()
                            datePickerState.selectedDateMillis?.let {
                                viewModel.setTarget(mantraId, malasInt, Date(it))
                            }
                            showDialog = false
                            targetMalasError = null
                        } catch (e: NumberFormatException) {
                            targetMalasError = context.getString(R.string.please_enter_a_valid_number)
                        }
                    }) {
                        Text(text = stringResource(id = R.string.set))
                    }
                }
            ) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    DatePicker(state = datePickerState)
                    TextField(
                        value = targetMalas,
                        onValueChange = { targetMalas = it },
                        label = { Text(stringResource(id = R.string.target_malas)) },
                        isError = targetMalasError != null,
                        modifier = Modifier.fillMaxWidth()
                    )
                    targetMalasError?.let {
                        Text(text = it, color = MaterialTheme.colorScheme.error)
                    }
                }
            }
        }
    }
}
