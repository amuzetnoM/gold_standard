package com.goldstandard.data.network

import retrofit2.http.GET
import retrofit2.http.Query

/**
 * Retrofit service interface for Yahoo Finance gold chart API.
 * Fetches gold futures (GC=F) price data.
 */
interface GoldApiService {
    
    @GET("v8/finance/chart/GC=F")
    suspend fun getGoldChart(
        @Query("interval") interval: String = "1d",
        @Query("range") range: String = "3mo"
    ): GoldChartResponse
}
