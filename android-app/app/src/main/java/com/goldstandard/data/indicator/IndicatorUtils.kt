package com.goldstandard.data.indicator

import com.goldstandard.model.IndicatorValues
import kotlin.math.max

/**
 * Utility object for calculating technical indicators.
 * All calculations are performed in pure Kotlin.
 */
object IndicatorUtils {
    
    /**
     * Calculates Simple Moving Average (SMA) for a list of prices.
     * @param prices List of price values
     * @param period The period for SMA calculation (e.g., 14, 50, 200)
     * @return SMA value or 0f if not enough data
     */
    fun calculateSMA(prices: List<Float>, period: Int = 14): Float {
        if (prices.isEmpty() || prices.size < period) return 0f
        return prices.takeLast(period).average().toFloat()
    }
    
    /**
     * Calculates Simple Moving Average series for chart overlay.
     * @param prices List of price values
     * @param period The period for SMA calculation
     * @return List of SMA values aligned with the input prices
     */
    fun calculateSMASeries(prices: List<Float>, period: Int = 14): List<Float> {
        if (prices.size < period) return emptyList()
        
        val smaList = mutableListOf<Float>()
        for (i in period - 1 until prices.size) {
            val sum = prices.subList(i - period + 1, i + 1).sum()
            smaList.add(sum / period)
        }
        return smaList
    }
    
    /**
     * Calculates Relative Strength Index (RSI).
     * @param prices List of price values
     * @param period The period for RSI calculation (default 14)
     * @return RSI value between 0 and 100, or 50f if not enough data
     */
    fun calculateRSI(prices: List<Float>, period: Int = 14): Float {
        if (prices.size < period + 1) return 50f
        
        val changes = mutableListOf<Float>()
        for (i in 1 until prices.size) {
            changes.add(prices[i] - prices[i - 1])
        }
        
        if (changes.size < period) return 50f
        
        val recentChanges = changes.takeLast(period)
        
        var avgGain = 0f
        var avgLoss = 0f
        
        for (change in recentChanges) {
            if (change > 0) avgGain += change
            else avgLoss += -change
        }
        
        avgGain /= period
        avgLoss /= period
        
        if (avgLoss == 0f) return 100f
        
        val rs = avgGain / avgLoss
        return 100 - (100 / (1 + rs))
    }
    
    /**
     * Calculates RSI series for chart overlay.
     * @param prices List of price values
     * @param period The period for RSI calculation
     * @return List of RSI values
     */
    fun calculateRSISeries(prices: List<Float>, period: Int = 14): List<Float> {
        if (prices.size < period + 1) return emptyList()
        
        val rsiList = mutableListOf<Float>()
        
        // Calculate changes
        val changes = mutableListOf<Float>()
        for (i in 1 until prices.size) {
            changes.add(prices[i] - prices[i - 1])
        }
        
        // Initial average gain/loss
        var avgGain = 0f
        var avgLoss = 0f
        
        for (i in 0 until period) {
            val change = changes[i]
            if (change > 0) avgGain += change
            else avgLoss += -change
        }
        
        avgGain /= period
        avgLoss /= period
        
        // First RSI
        val rs = if (avgLoss == 0f) Float.MAX_VALUE else avgGain / avgLoss
        rsiList.add(100 - (100 / (1 + rs)))
        
        // Smoothed RSI for remaining periods
        for (i in period until changes.size) {
            val change = changes[i]
            val gain = max(change, 0f)
            val loss = max(-change, 0f)
            
            avgGain = (avgGain * (period - 1) + gain) / period
            avgLoss = (avgLoss * (period - 1) + loss) / period
            
            val smoothedRS = if (avgLoss == 0f) Float.MAX_VALUE else avgGain / avgLoss
            rsiList.add(100 - (100 / (1 + smoothedRS)))
        }
        
        return rsiList
    }
    
    /**
     * Calculates both SMA and RSI indicators.
     * @param prices List of price values
     * @return IndicatorValues containing RSI and SMA
     */
    fun calculateIndicators(prices: List<Float>): IndicatorValues {
        return IndicatorValues(
            rsi = calculateRSI(prices),
            sma = calculateSMA(prices)
        )
    }
}
