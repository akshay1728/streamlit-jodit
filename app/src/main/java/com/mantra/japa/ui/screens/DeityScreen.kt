package com.mantra.japa.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
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
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.mantra.japa.R
import com.mantra.japa.ui.theme.SoothingBlue
import com.mantra.japa.ui.viewmodel.MainViewModel

@Composable
fun DeityScreen(
    viewModel: MainViewModel,
    onNavigateToMantra: () -> Unit,
    onNavigateToStatistics: () -> Unit
) {
    val deities by viewModel.deities.collectAsState()
    var newDeityName by remember { mutableStateOf("") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = stringResource(id = R.string.deities), style = MaterialTheme.typography.headlineMedium)

        if (deities.isEmpty()) {
            Text(text = stringResource(id = R.string.no_deities_added_yet))
        } else {
            LazyColumn(
                modifier = Modifier.weight(1f)
            ) {
                items(deities) { deity ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp),
                        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                        colors = CardDefaults.cardColors(containerColor = SoothingBlue)
                    ) {
                        Text(
                            text = deity.name,
                            modifier = Modifier.padding(16.dp),
                            style = MaterialTheme.typography.bodyLarge
                        )
                    }
                }
            }
        }

        TextField(
            value = newDeityName,
            onValueChange = { newDeityName = it },
            label = { Text(stringResource(id = R.string.new_deity_name)) },
            modifier = Modifier.fillMaxWidth()
        )
        Button(
            onClick = {
                viewModel.addDeity(newDeityName)
                newDeityName = ""
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text(text = stringResource(id = R.string.add_deity))
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            Button(onClick = onNavigateToMantra) {
                Text(text = stringResource(id = R.string.go_to_mantras))
            }
            Button(onClick = onNavigateToStatistics) {
                Text(text = stringResource(id = R.string.go_to_statistics))
            }
        }
    }
}
