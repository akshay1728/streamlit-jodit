package com.mantra.japa

import android.app.Application
import androidx.room.Room
import com.mantra.japa.data.db.MantraDatabase

class MantraJapaApplication : Application() {
    val database: MantraDatabase by lazy {
        Room.databaseBuilder(
            this,
            MantraDatabase::class.java, "mantra-database"
        ).fallbackToDestructiveMigration().build()
    }
}
