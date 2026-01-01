package com.mantra.japa.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "japa_entries")
data class JapaEntry(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val mantraId: Long,
    val malas: Int,
    val timestamp: Date
)
