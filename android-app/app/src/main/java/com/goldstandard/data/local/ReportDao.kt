package com.goldstandard.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.goldstandard.model.Report
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for Report entity.
 * Provides database operations for reports.
 */
@Dao
interface ReportDao {
    
    @Query("SELECT * FROM reports ORDER BY date DESC")
    fun getAllReports(): Flow<List<Report>>
    
    @Query("SELECT * FROM reports WHERE id = :id")
    suspend fun getReportById(id: Int): Report?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(report: Report)
    
    @Query("DELETE FROM reports WHERE id = :id")
    suspend fun deleteById(id: Int)
    
    @Query("DELETE FROM reports")
    suspend fun deleteAll()
}
