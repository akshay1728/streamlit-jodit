package com.mantra.japa.ui.screens

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.BarChart
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.List
import androidx.compose.material.icons.filled.Notes
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import android.widget.Toast
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.platform.LocalContext
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.mantra.japa.ui.navigation.NavGraph
import com.mantra.japa.ui.viewmodel.MainViewModel

sealed class BottomNavItem(val route: String, val icon: ImageVector, val label: String) {
    object Mantras : BottomNavItem("mantra", Icons.Default.List, "Mantras")
    object Deities : BottomNavItem("deity", Icons.Default.Home, "Deities")
    object Statistics : BottomNavItem("statistics", Icons.Default.BarChart, "Statistics")
    object Notes : BottomNavItem("notes", Icons.Default.Notes, "Notes")
}

@Composable
fun MainScreen(viewModel: MainViewModel) {
    val navController = rememberNavController()
    val context = LocalContext.current
    LaunchedEffect(Unit) {
        viewModel.saveEvents.collect {
            Toast.makeText(context, it, Toast.LENGTH_SHORT).show()
        }
    }
    val items = listOf(
        BottomNavItem.Mantras,
        BottomNavItem.Deities,
        BottomNavItem.Statistics,
        BottomNavItem.Notes,
    )

    Scaffold(
        bottomBar = {
            NavigationBar {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentDestination = navBackStackEntry?.destination
                items.forEach { screen ->
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = null) },
                        label = { Text(screen.label) },
                        selected = currentDestination?.hierarchy?.any { it.route == screen.route } == true,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { innerPadding ->
        NavGraph(
            viewModel = viewModel,
            navController = navController,
            startDestination = BottomNavItem.Mantras.route,
            modifier = Modifier.padding(innerPadding)
        )
    }
}
