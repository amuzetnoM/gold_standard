package com.goldstandard.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.goldstandard.data.repository.GoldRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the Dashboard screen.
 */
data class DashboardState(
    val price: Float = 0f,
    val previousClose: Float = 0f,
    val changePercent: Float = 0f,
    val isLoading: Boolean = false,
    val error: String? = null
)

/**
 * ViewModel for the Dashboard screen.
 * Manages gold price data and refresh operations.
 */
@HiltViewModel
class DashboardViewModel @Inject constructor(
    private val repository: GoldRepository
) : ViewModel() {
    
    private val _state = MutableStateFlow(DashboardState())
    val state: StateFlow<DashboardState> = _state.asStateFlow()
    
    init {
        fetchGoldPrice()
    }
    
    /**
     * Fetches the current gold price and calculates change percentage.
     */
    fun fetchGoldPrice() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)
            
            try {
                val currentPrice = repository.getCurrentGoldPrice()
                val previousClose = repository.getPreviousClose()
                
                if (currentPrice != null && previousClose != null) {
                    val changePercent = ((currentPrice - previousClose) / previousClose) * 100
                    _state.value = _state.value.copy(
                        price = currentPrice,
                        previousClose = previousClose,
                        changePercent = changePercent,
                        isLoading = false
                    )
                } else {
                    _state.value = _state.value.copy(
                        isLoading = false,
                        error = "Failed to fetch gold price"
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
     * Refresh gold price data.
     */
    fun refresh() {
        fetchGoldPrice()
    }
}
