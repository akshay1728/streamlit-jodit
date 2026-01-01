package com.mantra.japa.ui.screens

import androidx.compose.foundation.clickable
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
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.ExposedDropdownMenuBox
import androidx.compose.material3.ExposedDropdownMenuDefaults
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
import com.mantra.japa.data.model.Deity
import com.mantra.japa.ui.theme.CalmingGreen
import com.mantra.japa.ui.viewmodel.MainViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MantraScreen(
    viewModel: MainViewModel,
    onNavigateToDeity: () -> Unit,
    onNavigateToJapa: (Long) -> Unit
) {
    val mantras by viewModel.mantras.collectAsState()
    val deities by viewModel.deities.collectAsState()
    var newMantraName by remember { mutableStateOf("") }
    var expanded by remember { mutableStateOf(false) }
    var selectedDeity by remember { mutableStateOf<Deity?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = stringResource(id = R.string.mantras), style = MaterialTheme.typography.headlineMedium)

        if (mantras.isEmpty()) {
            Text(text = stringResource(id = R.string.no_mantras_added_yet))
        } else {
            LazyColumn(
                modifier = Modifier.weight(1f)
            ) {
                items(mantras) { mantra ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp)
                            .clickable { onNavigateToJapa(mantra.id) },
                        elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                        colors = CardDefaults.cardColors(containerColor = CalmingGreen)
                    ) {
                        Text(
                            text = mantra.name,
                            modifier = Modifier.padding(16.dp),
                            style = MaterialTheme.typography.bodyLarge
                        )
                    }
                }
            }
        }

        TextField(
            value = newMantraName,
            onValueChange = { newMantraName = it },
            label = { Text(stringResource(id = R.string.new_mantra_name)) },
            modifier = Modifier.fillMaxWidth()
        )

        ExposedDropdownMenuBox(
            expanded = expanded,
            onExpandedChange = { expanded = !expanded },
            modifier = Modifier.fillMaxWidth()
        ) {
            TextField(
                value = selectedDeity?.name ?: "",
                onValueChange = {},
                readOnly = true,
                label = { Text(stringResource(id = R.string.deity)) },
                trailingIcon = {
                    ExposedDropdownMenuDefaults.TrailingIcon(expanded = expanded)
                },
                modifier = Modifier.menuAnchor()
            )
            ExposedDropdownMenu(
                expanded = expanded,
                onDismissRequest = { expanded = false }
            ) {
                deities.forEach { deity ->
                    DropdownMenuItem(
                        text = { Text(deity.name) },
                        onClick = {
                            selectedDeity = deity
                            expanded = false
                        }
                    )
                }
            }
        }

        Button(
            onClick = {
                selectedDeity?.let {
                    viewModel.addMantra(newMantraName, it.id)
                    newMantraName = ""
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 8.dp)
        ) {
            Text(text = stringResource(id = R.string.add_mantra))
        }

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            Button(onClick = onNavigateToDeity) {
                Text(text = stringResource(id = R.string.go_to_deities))
            }
        }
    }
}
