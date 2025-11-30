package com.goldstandard.model

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Represents a saved report entity.
 * Stored locally using Room database.
 */
@Entity(tableName = "reports")
data class Report(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val title: String,
    val date: Long,
    val content: String
)
