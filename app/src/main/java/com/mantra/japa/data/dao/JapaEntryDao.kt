package com.mantra.japa.data.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import com.mantra.japa.data.model.JapaEntry
import kotlinx.coroutines.flow.Flow

@Dao
interface JapaEntryDao {
    @Insert
    suspend fun insert(japaEntry: JapaEntry)

    @Query("SELECT * FROM japa_entries WHERE mantraId = :mantraId")
    fun getJapaEntriesForMantra(mantraId: Long): Flow<List<JapaEntry>>

    @Query("SELECT * FROM japa_entries")
    fun getAllJapaEntries(): Flow<List<JapaEntry>>
}
