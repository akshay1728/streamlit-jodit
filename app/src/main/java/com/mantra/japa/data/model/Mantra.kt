package com.mantra.japa.data.model

import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "mantras",
    foreignKeys = [
        ForeignKey(
            entity = Deity::class,
            parentColumns = ["id"],
            childColumns = ["deityId"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index(value = ["deityId"])]
)
data class Mantra(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val name: String,
    val deityId: Long
)
