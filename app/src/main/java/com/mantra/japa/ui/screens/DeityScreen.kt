package com.mantra.japa.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material3.AlertDialog
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
import com.mantra.japa.data.model.Deity
import androidx.compose.foundation.layout.Row
import com.mantra.japa.ui.viewmodel.MainViewModel

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DeityScreen(viewModel: MainViewModel) {
    val deities by viewModel.deities.collectAsState()
    var newDeityName by remember { mutableStateOf("") }
    var showDeleteDialog by remember { mutableStateOf<Deity?>(null) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        if (deities.isEmpty()) {
            Text(text = stringResource(id = R.string.no_deities_added_yet))
        } else {
            LazyColumn(modifier = Modifier.weight(1f)) {
                items(deities) { deity ->
                    Card(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 4.dp)
                    ) {
                        Row(modifier = Modifier.padding(16.dp)) {
                            Text(
                                text = deity.name,
                                style = MaterialTheme.typography.bodyLarge,
                                modifier = Modifier.weight(1f)
                            )
                            IconButton(onClick = { showDeleteDialog = deity }) {
                                Icon(Icons.Default.Delete, contentDescription = "Delete Deity")
                            }
                        }
                    }
                }
            }
        }

        if (showDeleteDialog != null) {
            AlertDialog(
                onDismissRequest = { showDeleteDialog = null },
                title = { Text("Delete Deity") },
                text = { Text("Are you sure you want to delete this deity? This will also delete all associated mantras and notes.") },
                confirmButton = {
                    Button(
                        onClick = {
                            viewModel.deleteDeity(showDeleteDialog!!)
                            showDeleteDialog = null
                        }
                    ) {
                        Text("Delete")
                    }
                },
                dismissButton = {
                    Button(onClick = { showDeleteDialog = null }) {
                        Text("Cancel")
                    }
                }
            )
        }
        Spacer(modifier = Modifier.height(16.dp))
        TextField(
            value = newDeityName,
            onValueChange = { newDeityName = it },
            label = { Text(stringResource(id = R.string.new_deity_name)) },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        Button(
            onClick = {
                if (newDeityName.isNotBlank()) {
                    viewModel.addDeity(newDeityName)
                    newDeityName = ""
                }
            },
            enabled = newDeityName.isNotBlank()
        ) {
            Text(text = stringResource(id = R.string.add_deity))
        }
    }
}
