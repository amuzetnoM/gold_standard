package com.goldstandard.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.goldstandard.model.Report

/**
 * Room database for local data persistence.
 * Contains the Report entity table.
 */
@Database(
    entities = [Report::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    
    abstract fun reportDao(): ReportDao
    
    companion object {
        const val DATABASE_NAME = "gold_standard_db"
    }
}
