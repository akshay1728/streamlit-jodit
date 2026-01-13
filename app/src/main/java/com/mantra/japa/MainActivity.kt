package com.mantra.japa

import android.content.Context
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
import androidx.room.RoomDatabase
import androidx.sqlite.db.SupportSQLiteDatabase
import com.mantra.japa.data.db.MantraDatabase
import com.mantra.japa.data.model.Deity
import com.mantra.japa.data.model.Mantra
import com.mantra.japa.ui.screens.LoadingScreen
import com.mantra.japa.ui.screens.MainScreen
import com.mantra.japa.ui.theme.MantraJapaTrackerTheme
import com.mantra.japa.ui.viewmodel.MainViewModel
import com.mantra.japa.ui.viewmodel.ViewModelFactory
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : ComponentActivity() {

    private var viewModel: MainViewModel? by mutableStateOf(null)
    private lateinit var database: MantraDatabase

    private class RsvpDatabaseCallback(
        private val provider: () -> MantraDatabase,
        private val scope: CoroutineScope
    ) : RoomDatabase.Callback() {
        override fun onCreate(db: SupportSQLiteDatabase) {
            super.onCreate(db)
            scope.launch {
                val db = provider()
                val deityDao = db.deityDao()
                val mantraDao = db.mantraDao()

                val deityId = deityDao.insert(Deity(name = "Kaal Bhairav"))
                mantraDao.insert(Mantra(name = "Om Bhairavaaya Namah", deityId = deityId))
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            withContext(Dispatchers.IO) {
                database = Room.databaseBuilder(
                    applicationContext,
                    MantraDatabase::class.java, "mantra-database"
                )
                    .addCallback(RsvpDatabaseCallback({ database }, this))
                    .fallbackToDestructiveMigration()
                    .build()
            }
            val viewModelFactory = ViewModelFactory(database.mantraDao(), database.deityDao(), database.japaEntryDao(), database.noteDao())
            viewModel = ViewModelProvider(this@MainActivity, viewModelFactory)[MainViewModel::class.java]
        }

        setContent {
            MantraJapaTrackerTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    if (viewModel != null) {
                        MainScreen(viewModel = viewModel!!)
                    } else {
                        LoadingScreen()
                    }
                }
            }
        }
    }
}
