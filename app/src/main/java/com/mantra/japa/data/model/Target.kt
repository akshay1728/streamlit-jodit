package com.mantra.japa.data.model

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import java.util.Date

@Entity(tableName = "targets", indices = [Index(value = ["mantraId"], unique = true)])
data class Target(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val mantraId: Long,
    val targetMalas: Int,
    val targetDate: Date
)
