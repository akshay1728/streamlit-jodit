package com.mantra.japa.data.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.Query
import androidx.room.Update
import com.mantra.japa.data.model.Mantra
import kotlinx.coroutines.flow.Flow

@Dao
interface MantraDao {
    @Insert
    suspend fun insert(mantra: Mantra)

    @Update
    suspend fun update(mantra: Mantra)

    @Query("SELECT * FROM mantras")
    fun getAllMantras(): Flow<List<Mantra>>

    @Query("SELECT * FROM mantras WHERE id = :id")
    suspend fun getMantraById(id: Long): Mantra?
}
