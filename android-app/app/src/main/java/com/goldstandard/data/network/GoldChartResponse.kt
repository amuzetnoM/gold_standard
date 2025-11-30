package com.goldstandard.data.network

import com.google.gson.annotations.SerializedName

/**
 * Data transfer objects for Yahoo Finance API responses.
 */
data class GoldChartResponse(
    @SerializedName("chart")
    val chart: ChartData?
)

data class ChartData(
    @SerializedName("result")
    val result: List<ChartResult>?,
    @SerializedName("error")
    val error: ChartError?
)

data class ChartResult(
    @SerializedName("meta")
    val meta: ChartMeta?,
    @SerializedName("timestamp")
    val timestamps: List<Long>?,
    @SerializedName("indicators")
    val indicators: Indicators?
)

data class ChartMeta(
    @SerializedName("currency")
    val currency: String?,
    @SerializedName("symbol")
    val symbol: String?,
    @SerializedName("regularMarketPrice")
    val regularMarketPrice: Float?,
    @SerializedName("previousClose")
    val previousClose: Float?
)

data class Indicators(
    @SerializedName("quote")
    val quote: List<Quote>?
)

data class Quote(
    @SerializedName("open")
    val open: List<Float?>?,
    @SerializedName("high")
    val high: List<Float?>?,
    @SerializedName("low")
    val low: List<Float?>?,
    @SerializedName("close")
    val close: List<Float?>?,
    @SerializedName("volume")
    val volume: List<Long?>?
)

data class ChartError(
    @SerializedName("code")
    val code: String?,
    @SerializedName("description")
    val description: String?
)
