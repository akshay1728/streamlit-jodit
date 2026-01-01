package com.mantra.japa.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.mantra.japa.R
import com.mantra.japa.ui.theme.LightGray
import com.mantra.japa.ui.viewmodel.MainViewModel

@Composable
fun StatisticsScreen(
    viewModel: MainViewModel
) {
    val statistics by viewModel.statistics.collectAsState()
    val deityStatistics by viewModel.deityStatistics.collectAsState()
    var tabIndex by remember { mutableStateOf(0) }
    val tabs = listOf(stringResource(id = R.string.mantra), stringResource(id = R.string.deity))

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(text = stringResource(id = R.string.statistics), style = MaterialTheme.typography.headlineMedium)

        TabRow(selectedTabIndex = tabIndex) {
            tabs.forEachIndexed { index, title ->
                Tab(text = { Text(title) },
                    selected = tabIndex == index,
                    onClick = { tabIndex = index }
                )
            }
        }
        when (tabIndex) {
            0 -> MantraStatistics(statistics)
            1 -> DeityStatistics(deityStatistics)
        }
    }
}

@Composable
fun MantraStatistics(statistics: List<com.mantra.japa.data.model.Statistics>) {
    LazyColumn {
        items(statistics) { statistic ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                colors = CardDefaults.cardColors(containerColor = LightGray)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = stringResource(id = R.string.mantra_label, statistic.mantra.name), style = MaterialTheme.typography.titleLarge)
                    Text(text = stringResource(id = R.string.deity_label, statistic.deity.name), style = MaterialTheme.typography.titleMedium)
                    Text(text = stringResource(id = R.string.total_malas, statistic.totalMalas), style = MaterialTheme.typography.bodyLarge)
                    Text(text = stringResource(id = R.string.total_japas, statistic.totalJapas), style = MaterialTheme.typography.bodyLarge)
                }
            }
        }
    }
}

@Composable
fun DeityStatistics(deityStatistics: List<com.mantra.japa.data.model.DeityStatistics>) {
    LazyColumn {
        items(deityStatistics) { statistic ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 8.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp),
                colors = CardDefaults.cardColors(containerColor = LightGray)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(text = stringResource(id = R.string.deity_label, statistic.deity.name), style = MaterialTheme.typography.titleLarge)
                    Text(text = stringResource(id = R.string.total_malas, statistic.totalMalas), style = MaterialTheme.typography.bodyLarge)
                    Text(text = stringResource(id = R.string.total_japas, statistic.totalJapas), style = MaterialTheme.typography.bodyLarge)
                }
            }
        }
    }
}
