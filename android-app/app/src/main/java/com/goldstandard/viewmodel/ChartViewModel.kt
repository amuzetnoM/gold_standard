package com.goldstandard.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.goldstandard.data.repository.GoldRepository
import com.goldstandard.model.IndicatorValues
import com.goldstandard.model.Price
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the Chart screen.
 */
data class ChartState(
    val prices: List<Price> = emptyList(),
    val smaSeries: List<Float> = emptyList(),
    val rsiSeries: List<Float> = emptyList(),
    val indicators: IndicatorValues = IndicatorValues(50f, 0f),
    val showSMA: Boolean = true,
    val showRSI: Boolean = false,
    val selectedRange: String = "3mo",
    val isLoading: Boolean = false,
    val error: String? = null
)

/**
 * ViewModel for the Chart screen.
 * Manages historical price data and indicator overlays.
 */
@HiltViewModel
class ChartViewModel @Inject constructor(
    private val repository: GoldRepository
) : ViewModel() {
    
    private val _state = MutableStateFlow(ChartState())
    val state: StateFlow<ChartState> = _state.asStateFlow()
    
    init {
        fetchChartData()
    }
    
    /**
     * Fetches historical price data and calculates indicators.
     */
    fun fetchChartData() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)
            
            try {
                val prices = repository.getHistoricalPrices(
                    range = _state.value.selectedRange
                )
                
                if (prices.isNotEmpty()) {
                    val smaSeries = repository.calculateSMASeries(prices, period = 14)
                    val rsiSeries = repository.calculateRSISeries(prices, period = 14)
                    val indicators = repository.calculateIndicators(prices)
                    
                    _state.value = _state.value.copy(
                        prices = prices,
                        smaSeries = smaSeries,
                        rsiSeries = rsiSeries,
                        indicators = indicators,
                        isLoading = false
                    )
                } else {
                    _state.value = _state.value.copy(
                        isLoading = false,
                        error = "No price data available"
                    )
                }
            } catch (e: Exception) {
                _state.value = _state.value.copy(
                    isLoading = false,
                    error = e.message ?: "Unknown error"
                )
            }
        }
    }
    
    /**
     * Toggles SMA overlay visibility.
     */
    fun toggleSMA() {
        _state.value = _state.value.copy(showSMA = !_state.value.showSMA)
    }
    
    /**
     * Toggles RSI overlay visibility.
     */
    fun toggleRSI() {
        _state.value = _state.value.copy(showRSI = !_state.value.showRSI)
    }
    
    /**
     * Changes the time range for chart data.
     */
    fun setRange(range: String) {
        _state.value = _state.value.copy(selectedRange = range)
        fetchChartData()
    }
    
    /**
     * Refresh chart data.
     */
    fun refresh() {
        fetchChartData()
    }
}
