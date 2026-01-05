package com.mantra.japa.data.model

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey
import java.util.Date

@Entity(
    tableName = "japa_entries",
    foreignKeys = [
        ForeignKey(
            entity = Mantra::class,
            parentColumns = ["id"],
            childColumns = ["mantraId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index(value = ["mantraId"])]
)
data class JapaEntry(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val mantraId: Long,
    val malas: Int,
    val timestamp: Date
)
