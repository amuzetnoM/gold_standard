package com.goldstandard.model

/**
 * Represents a price point with timestamp and value.
 * Used for historical price data and chart visualization.
 */
data class Price(
    val timestamp: Long,
    val value: Float
)
