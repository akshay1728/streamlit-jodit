package com.mantra.japa.data.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.mantra.japa.data.model.Target
import kotlinx.coroutines.flow.Flow

@Dao
interface TargetDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(target: Target)

    @Update
    suspend fun update(target: Target)

    @Query("SELECT * FROM targets WHERE mantraId = :mantraId")
    fun getTargetForMantra(mantraId: Long): Flow<Target?>
}
