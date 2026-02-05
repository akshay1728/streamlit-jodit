package com.mantra.japa.data.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.Query
import com.mantra.japa.data.model.Deity
import kotlinx.coroutines.flow.Flow

@Dao
interface DeityDao {
    @Insert
    suspend fun insert(deity: Deity): Long

    @Delete
    suspend fun delete(deity: Deity)

    @Query("SELECT * FROM deities")
    fun getAllDeities(): Flow<List<Deity>>
}
