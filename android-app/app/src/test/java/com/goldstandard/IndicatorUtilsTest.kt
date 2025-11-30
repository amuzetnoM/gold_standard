package com.goldstandard

import com.goldstandard.data.indicator.IndicatorUtils
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

/**
 * Unit tests for IndicatorUtils.
 */
class IndicatorUtilsTest {
    
    @Test
    fun `calculateSMA returns correct average`() {
        val prices = listOf(10f, 20f, 30f, 40f, 50f)
        val result = IndicatorUtils.calculateSMA(prices, period = 5)
        assertEquals(30f, result, 0.001f)
    }
    
    @Test
    fun `calculateSMA with insufficient data returns zero`() {
        val prices = listOf(10f, 20f)
        val result = IndicatorUtils.calculateSMA(prices, period = 5)
        assertEquals(0f, result, 0.001f)
    }
    
    @Test
    fun `calculateSMA with empty list returns zero`() {
        val prices = emptyList<Float>()
        val result = IndicatorUtils.calculateSMA(prices, period = 5)
        assertEquals(0f, result, 0.001f)
    }
    
    @Test
    fun `calculateSMASeries returns correct length`() {
        val prices = listOf(10f, 20f, 30f, 40f, 50f, 60f, 70f)
        val result = IndicatorUtils.calculateSMASeries(prices, period = 3)
        // 7 prices with period 3 = 5 SMA values (indices 2-6)
        assertEquals(5, result.size)
    }
    
    @Test
    fun `calculateSMASeries first value is correct`() {
        val prices = listOf(10f, 20f, 30f, 40f, 50f)
        val result = IndicatorUtils.calculateSMASeries(prices, period = 3)
        // First SMA = (10+20+30)/3 = 20
        assertEquals(20f, result[0], 0.001f)
    }
    
    @Test
    fun `calculateRSI returns 50 with insufficient data`() {
        val prices = listOf(10f, 20f)
        val result = IndicatorUtils.calculateRSI(prices, period = 14)
        assertEquals(50f, result, 0.001f)
    }
    
    @Test
    fun `calculateRSI returns value between 0 and 100`() {
        val prices = (1..30).map { it.toFloat() }
        val result = IndicatorUtils.calculateRSI(prices, period = 14)
        assertTrue(result in 0f..100f)
    }
    
    @Test
    fun `calculateRSI returns 100 when only gains`() {
        // All positive changes
        val prices = listOf(10f, 11f, 12f, 13f, 14f, 15f, 16f, 17f, 18f, 19f, 20f, 21f, 22f, 23f, 24f, 25f)
        val result = IndicatorUtils.calculateRSI(prices, period = 14)
        assertEquals(100f, result, 0.001f)
    }
    
    @Test
    fun `calculateRSISeries returns empty with insufficient data`() {
        val prices = listOf(10f, 20f)
        val result = IndicatorUtils.calculateRSISeries(prices, period = 14)
        assertTrue(result.isEmpty())
    }
    
    @Test
    fun `calculateRSISeries values are between 0 and 100`() {
        val prices = (1..50).map { it.toFloat() + (it % 3) * 2 }
        val result = IndicatorUtils.calculateRSISeries(prices, period = 14)
        assertTrue(result.all { it in 0f..100f })
    }
    
    @Test
    fun `calculateIndicators returns both RSI and SMA`() {
        val prices = (1..30).map { it.toFloat() }
        val result = IndicatorUtils.calculateIndicators(prices)
        
        assertTrue(result.rsi in 0f..100f)
        assertTrue(result.sma > 0f)
    }
}
