package com.mantra.japa.data.db

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.mantra.japa.data.dao.DeityDao
import com.mantra.japa.data.dao.JapaEntryDao
import com.mantra.japa.data.dao.MantraDao
import com.mantra.japa.data.dao.NoteDao
import com.mantra.japa.data.model.Deity
import com.mantra.japa.data.model.JapaEntry
import com.mantra.japa.data.model.Mantra
import com.mantra.japa.data.model.Note
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch

@Database(entities = [Mantra::class, Deity::class, JapaEntry::class, Note::class], version = 3, exportSchema = false)
@TypeConverters(Converters::class)
abstract class MantraDatabase : RoomDatabase() {
    abstract fun mantraDao(): MantraDao
    abstract fun deityDao(): DeityDao
    abstract fun japaEntryDao(): JapaEntryDao
    abstract fun noteDao(): NoteDao

    companion object {
        @Volatile
        private var INSTANCE: MantraDatabase? = null

        fun getDatabase(context: Context): MantraDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    MantraDatabase::class.java,
                    "mantra-database"
                )
                    .addMigrations(MIGRATION_2_3)
                    .addCallback(object : Callback() {
                        override fun onCreate(db: SupportSQLiteDatabase) {
                            super.onCreate(db)
                            INSTANCE?.let { database ->
                                CoroutineScope(Dispatchers.IO).launch {
                                    val deityDao = database.deityDao()
                                    val mantraDao = database.mantraDao()

                                    val deityId = deityDao.insert(Deity(name = "Kaal Bhairav"))
                                    mantraDao.insert(Mantra(name = "Om Bhairavaaya Namah", deityId = deityId))
                                }
                            }
                        }
                    })
                    .build()
                INSTANCE = instance
                instance
            }
        }

        private val MIGRATION_2_3 = object : Migration(2, 3) {
            override fun migrate(database: SupportSQLiteDatabase) {
                database.execSQL("ALTER TABLE mantras ADD COLUMN lastUpdated INTEGER")
            }
        }
    }
}
