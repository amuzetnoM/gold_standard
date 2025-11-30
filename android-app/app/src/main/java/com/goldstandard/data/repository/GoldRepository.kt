package com.goldstandard.data.repository

import com.goldstandard.data.indicator.IndicatorUtils
import com.goldstandard.data.local.ReportDao
import com.goldstandard.data.network.GoldApiService
import com.goldstandard.model.IndicatorValues
import com.goldstandard.model.Price
import com.goldstandard.model.Report
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for coordinating data operations between network and local sources.
 * Provides a clean API for ViewModels to access data.
 */
@Singleton
class GoldRepository @Inject constructor(
    private val api: GoldApiService,
    private val reportDao: ReportDao
) {
    
    /**
     * Fetches the current gold price from the API.
     * @return Current gold price or null if unavailable
     */
    suspend fun getCurrentGoldPrice(): Float? {
        return try {
            val response = api.getGoldChart(interval = "1d", range = "1d")
            response.chart?.result?.firstOrNull()?.meta?.regularMarketPrice
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Fetches the previous close price for calculating change percentage.
     * @return Previous close price or null if unavailable
     */
    suspend fun getPreviousClose(): Float? {
        return try {
            val response = api.getGoldChart(interval = "1d", range = "5d")
            response.chart?.result?.firstOrNull()?.meta?.previousClose
        } catch (e: Exception) {
            null
        }
    }
    
    /**
     * Fetches historical price data for chart display.
     * @param range Time range (e.g., "1mo", "3mo", "1y")
     * @param interval Data interval (e.g., "1d", "1h")
     * @return List of Price objects
     */
    suspend fun getHistoricalPrices(
        range: String = "3mo",
        interval: String = "1d"
    ): List<Price> {
        return try {
            val response = api.getGoldChart(interval = interval, range = range)
            val result = response.chart?.result?.firstOrNull() ?: return emptyList()
            
            val timestamps = result.timestamps ?: return emptyList()
            val closePrices = result.indicators?.quote?.firstOrNull()?.close ?: return emptyList()
            
            timestamps.zip(closePrices).mapNotNull { (timestamp, price) ->
                price?.let { Price(timestamp = timestamp, value = it) }
            }
        } catch (e: Exception) {
            emptyList()
        }
    }
    
    /**
     * Calculates technical indicators from price data.
     * @param prices List of Price objects
     * @return IndicatorValues containing RSI and SMA
     */
    fun calculateIndicators(prices: List<Price>): IndicatorValues {
        val values = prices.map { it.value }
        return IndicatorUtils.calculateIndicators(values)
    }
    
    /**
     * Calculates SMA series for chart overlay.
     * @param prices List of Price objects
     * @param period SMA period
     * @return List of SMA values
     */
    fun calculateSMASeries(prices: List<Price>, period: Int = 14): List<Float> {
        val values = prices.map { it.value }
        return IndicatorUtils.calculateSMASeries(values, period)
    }
    
    /**
     * Calculates RSI series for chart overlay.
     * @param prices List of Price objects
     * @param period RSI period
     * @return List of RSI values
     */
    fun calculateRSISeries(prices: List<Price>, period: Int = 14): List<Float> {
        val values = prices.map { it.value }
        return IndicatorUtils.calculateRSISeries(values, period)
    }
    
    // Report operations
    
    /**
     * Gets all reports as a Flow for reactive updates.
     */
    fun getReports(): Flow<List<Report>> = reportDao.getAllReports()
    
    /**
     * Gets a specific report by ID.
     */
    suspend fun getReportById(id: Int): Report? = reportDao.getReportById(id)
    
    /**
     * Saves a report to the local database.
     */
    suspend fun saveReport(report: Report) = reportDao.insert(report)
    
    /**
     * Deletes a report by ID.
     */
    suspend fun deleteReport(id: Int) = reportDao.deleteById(id)
}
