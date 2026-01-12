package com.mantra.japa.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
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
import com.mantra.japa.ui.viewmodel.DeityStatistics
import com.mantra.japa.ui.viewmodel.MainViewModel
import com.mantra.japa.ui.viewmodel.Statistics

@Composable
fun StatisticsScreen(viewModel: MainViewModel) {
    val statistics by viewModel.statistics.collectAsState()
    val deityStatistics by viewModel.deityStatistics.collectAsState()
    var selectedTabIndex by remember { mutableStateOf(0) }
    val tabs = listOf(stringResource(id = R.string.mantras), stringResource(id = R.string.deities))

    Column(modifier = Modifier.fillMaxSize()) {
        TabRow(selectedTabIndex = selectedTabIndex) {
            tabs.forEachIndexed { index, title ->
                Tab(
                    selected = selectedTabIndex == index,
                    onClick = { selectedTabIndex = index },
                    text = { Text(text = title) }
                )
            }
        }
        when (selectedTabIndex) {
            0 -> MantraStatisticsList(statistics)
            1 -> DeityStatisticsList(deityStatistics)
        }
    }
}

@Composable
fun MantraStatisticsList(statistics: List<Statistics>) {
    LazyColumn(modifier = Modifier.padding(16.dp)) {
        items(statistics) { stat ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = stat.mantra.name, style = MaterialTheme.typography.titleLarge)
                    Text(text = stat.deity.name, style = MaterialTheme.typography.titleMedium)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = stringResource(id = R.string.total_malas, stat.totalMalas))
                    Text(text = stringResource(id = R.string.total_japas, stat.totalJapas))
                }
            }
        }
    }
}

@Composable
fun DeityStatisticsList(deityStatistics: List<DeityStatistics>) {
    LazyColumn(modifier = Modifier.padding(16.dp)) {
        items(deityStatistics) { stat ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = stat.deity.name, style = MaterialTheme.typography.titleLarge)
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(text = stringResource(id = R.string.total_malas, stat.totalMalas))
                    Text(text = stringResource(id = R.string.total_japas, stat.totalJapas))
                }
            }
        }
    }
}
