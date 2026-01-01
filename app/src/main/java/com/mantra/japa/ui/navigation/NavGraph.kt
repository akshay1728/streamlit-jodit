package com.mantra.japa.ui.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.mantra.japa.ui.screens.DeityScreen
import com.mantra.japa.ui.screens.JapaScreen
import com.mantra.japa.ui.screens.MantraScreen
import com.mantra.japa.ui.screens.StatisticsScreen
import com.mantra.japa.ui.screens.TithiScreen
import com.mantra.japa.ui.viewmodel.MainViewModel

@Composable
fun NavGraph(
    viewModel: MainViewModel,
    startDestination: String = "deity"
) {
    val navController = rememberNavController()
    NavHost(navController = navController, startDestination = startDestination) {
        composable("deity") {
            DeityScreen(
                viewModel = viewModel,
                onNavigateToMantra = { navController.navigate("mantra") },
                onNavigateToStatistics = { navController.navigate("statistics") },
                onNavigateToTithi = { navController.navigate("tithi") }
            )
        }
        composable("mantra") {
            MantraScreen(
                viewModel = viewModel,
                onNavigateToDeity = { navController.navigate("deity") },
                onNavigateToJapa = { mantraId ->
                    navController.navigate("japa/$mantraId")
                }
            )
        }
        composable(
            "japa/{mantraId}",
            arguments = listOf(navArgument("mantraId") { type = NavType.LongType })
        ) { backStackEntry ->
            val mantraId = backStackEntry.arguments?.getLong("mantraId") ?: 0
            JapaScreen(viewModel = viewModel, mantraId = mantraId)
        }
        composable("statistics") {
            StatisticsScreen(viewModel = viewModel)
        }
        composable("tithi") {
            TithiScreen(viewModel = viewModel)
        }
    }
}
