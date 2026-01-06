package com.mantra.japa.ui.screens

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextField
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.mantra.japa.R
import com.mantra.japa.ui.viewmodel.MainViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MantraScreen(
    viewModel: MainViewModel,
    onNavigateToJapa: (Long) -> Unit
) {
    val mantras by viewModel.mantras.collectAsState()
    val deities by viewModel.deities.collectAsState()
    var newMantraName by remember { mutableStateOf("") }
    var selectedDeityId by remember { mutableStateOf<Long?>(null) }
    var expanded by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        if (mantras.isEmpty()) {
            Text(text = stringResource(id = R.string.no_mantras_added_yet))
        } else {
            LazyColumn(modifier = Modifier.weight(1f)) {
                items(mantras) { mantra ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp)
                            .clickable { onNavigateToJapa(mantra.id) }
                    ) {
                        Text(
                            text = mantra.name,
                            style = MaterialTheme.typography.bodyLarge,
                            modifier = Modifier.padding(16.dp)
                        )
                    }
                }
            }
        }
        Spacer(modifier = Modifier.height(16.dp))
        if (deities.isEmpty()) {
            Text(text = stringResource(id = R.string.no_deities_added_yet))
        } else {
            TextField(
                value = newMantraName,
                onValueChange = { newMantraName = it },
                label = { Text(stringResource(id = R.string.new_mantra_name)) },
                modifier = Modifier.fillMaxWidth()
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row {
                Button(onClick = { expanded = true }) {
                    Text(text = deities.find { it.id == selectedDeityId }?.name ?: stringResource(id = R.string.deity))
                }
                DropdownMenu(
                    expanded = expanded,
                    onDismissRequest = { expanded = false }
                ) {
                    deities.forEach { deity ->
                        DropdownMenuItem(
                            text = { Text(deity.name) },
                            onClick = {
                                selectedDeityId = deity.id
                                expanded = false
                            }
                        )
                    }
                }
            }
            Spacer(modifier = Modifier.height(8.dp))
            Button(
                onClick = {
                    if (newMantraName.isNotBlank() && selectedDeityId != null) {
                        viewModel.addMantra(newMantraName, selectedDeityId!!)
                        newMantraName = ""
                        selectedDeityId = null
                    }
                },
                enabled = newMantraName.isNotBlank() && selectedDeityId != null
            ) {
                Text(text = stringResource(id = R.string.add_mantra))
            }
        }
    }
}
