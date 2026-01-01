package com.mantra.japa.data.model

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "mantras")
data class Mantra(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val name: String,
    val deityId: Long
)
