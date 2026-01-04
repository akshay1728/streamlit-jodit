package com.mantra.japa.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
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
import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NotesScreen(viewModel: MainViewModel) {
    val notes by viewModel.notes.collectAsState()
    val filter by viewModel.notesFilter.collectAsState()
    val selectedYear by viewModel.selectedYear.collectAsState()
    val selectedMonth by viewModel.selectedMonth.collectAsState()

    var yearMenuExpanded by remember { mutableStateOf(false) }
    var monthMenuExpanded by remember { mutableStateOf(false) }

    val years = (2020..Calendar.getInstance().get(Calendar.YEAR)).toList()
    val months = (1..12).toList()

    Column(modifier = Modifier.padding(16.dp)) {
        TextField(
            value = filter,
            onValueChange = { viewModel.onNotesFilterChanged(it) },
            label = { Text(stringResource(id = R.string.filter_notes)) },
            modifier = Modifier.fillMaxWidth()
        )
        Spacer(modifier = Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(onClick = { yearMenuExpanded = true }) {
                Text(selectedYear?.toString() ?: stringResource(id = R.string.select_year))
            }
            DropdownMenu(
                expanded = yearMenuExpanded,
                onDismissRequest = { yearMenuExpanded = false }
            ) {
                DropdownMenuItem(
                    text = { Text(stringResource(id = R.string.all_years)) },
                    onClick = {
                        viewModel.onYearSelected(null)
                        yearMenuExpanded = false
                    }
                )
                years.forEach { year ->
                    DropdownMenuItem(
                        text = { Text(year.toString()) },
                        onClick = {
                            viewModel.onYearSelected(year)
                            yearMenuExpanded = false
                        }
                    )
                }
            }

            Button(onClick = { monthMenuExpanded = true }) {
                Text(selectedMonth?.toString() ?: stringResource(id = R.string.select_month))
            }
            DropdownMenu(
                expanded = monthMenuExpanded,
                onDismissRequest = { monthMenuExpanded = false }
            ) {
                DropdownMenuItem(
                    text = { Text(stringResource(id = R.string.all_months)) },
                    onClick = {
                        viewModel.onMonthSelected(null)
                        monthMenuExpanded = false
                    }
                )
                months.forEach { month ->
                    DropdownMenuItem(
                        text = { Text(month.toString()) },
                        onClick = {
                            viewModel.onMonthSelected(month)
                            monthMenuExpanded = false
                        }
                    )
                }
            }
        }

        LazyColumn(modifier = Modifier.padding(top = 16.dp)) {
            items(notes) { noteDetails ->
                Card(modifier = Modifier.padding(vertical = 8.dp).fillMaxWidth()) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            text = noteDetails.mantra.name,
                            style = MaterialTheme.typography.titleLarge
                        )
                        Text(
                            text = noteDetails.deity.name,
                            style = MaterialTheme.typography.titleMedium
                        )
                        Text(
                            text = noteDetails.note.text,
                            style = MaterialTheme.typography.bodyLarge
                        )
                        Text(
                            text = SimpleDateFormat(stringResource(id = R.string.date_format), Locale.getDefault()).format(noteDetails.note.timestamp),
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }
        }
    }
}
