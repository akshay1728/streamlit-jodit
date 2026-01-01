package com.mantra.japa

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import androidx.room.Room
import com.mantra.japa.data.db.MantraDatabase
import com.mantra.japa.ui.navigation.NavGraph
import com.mantra.japa.ui.screens.LoadingScreen
import com.mantra.japa.ui.theme.MantraJapaTrackerTheme
import com.mantra.japa.ui.viewmodel.MainViewModel
import com.mantra.japa.ui.viewmodel.ViewModelFactory
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {

    private var viewModel: MainViewModel? by mutableStateOf(null)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            val db = withContext(Dispatchers.IO) {
                Room.databaseBuilder(
                    applicationContext,
                    MantraDatabase::class.java, "mantra-database"
                ).build()
            }
            val viewModelFactory = ViewModelFactory(db.mantraDao(), db.deityDao(), db.japaEntryDao(), db.targetDao())
            viewModel = ViewModelProvider(this@MainActivity, viewModelFactory)[MainViewModel::class.java]
        }

        setContent {
            MantraJapaTrackerTheme {
                // A surface container using the 'background' color from the theme
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    if (viewModel != null) {
                        NavGraph(viewModel = viewModel!!)
                    } else {
                        LoadingScreen()
                    }
                }
            }
        }
    }
}
