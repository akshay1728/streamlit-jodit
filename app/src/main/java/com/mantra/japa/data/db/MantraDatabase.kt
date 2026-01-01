package com.mantra.japa.data.db

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.mantra.japa.data.dao.DeityDao
import com.mantra.japa.data.dao.JapaEntryDao
import com.mantra.japa.data.dao.MantraDao
import com.mantra.japa.data.dao.TargetDao
import com.mantra.japa.data.model.Deity
import com.mantra.japa.data.model.JapaEntry
import com.mantra.japa.data.model.Mantra
import com.mantra.japa.data.model.Target

@Database(entities = [Mantra::class, Deity::class, JapaEntry::class, Target::class], version = 1)
@TypeConverters(Converters::class)
abstract class MantraDatabase : RoomDatabase() {
    abstract fun mantraDao(): MantraDao
    abstract fun deityDao(): DeityDao
    abstract fun japaEntryDao(): JapaEntryDao
    abstract fun targetDao(): TargetDao
}
