package com.goldstandard.model

/**
 * Holds calculated technical indicator values.
 * RSI: Relative Strength Index (0-100)
 * SMA: Simple Moving Average
 */
data class IndicatorValues(
    val rsi: Float,
    val sma: Float
)
