package com.mantra.japa.ui.navigation

import androidx.compose.animation.fadeIn
import androidx.compose.animation.fadeOut
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.mantra.japa.ui.screens.DeityScreen
import com.mantra.japa.ui.screens.JapaScreen
import com.mantra.japa.ui.screens.MantraScreen
import com.mantra.japa.ui.screens.StatisticsScreen
import com.mantra.japa.ui.viewmodel.MainViewModel

@Composable
fun NavGraph(
    viewModel: MainViewModel,
    navController: NavHostController,
    modifier: Modifier = Modifier,
    startDestination: String = "mantra"
) {
    NavHost(
        navController = navController,
        startDestination = startDestination,
        modifier = modifier,
        enterTransition = { fadeIn() },
        exitTransition = { fadeOut() },
        popEnterTransition = { fadeIn() },
        popExitTransition = { fadeOut() }
    ) {
        composable("deity") {
            DeityScreen(
                viewModel = viewModel
            )
        }
        composable("mantra") {
            MantraScreen(
                viewModel = viewModel,
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
            JapaScreen(viewModel = viewModel, mantraId = mantraId, navController = navController)
        }
        composable("statistics") {
            StatisticsScreen(viewModel = viewModel)
        }
    }
}
