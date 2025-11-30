package com.goldstandard.viewmodel

import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.goldstandard.data.repository.GoldRepository
import com.goldstandard.model.Report
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the Report Detail screen.
 */
data class ReportDetailState(
    val report: Report? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)

/**
 * ViewModel for the Report Detail screen.
 * Manages a single report's data.
 */
@HiltViewModel
class ReportDetailViewModel @Inject constructor(
    private val repository: GoldRepository,
    savedStateHandle: SavedStateHandle
) : ViewModel() {
    
    private val reportId: Int = savedStateHandle["reportId"] ?: 0
    
    private val _state = MutableStateFlow(ReportDetailState())
    val state: StateFlow<ReportDetailState> = _state.asStateFlow()
    
    init {
        loadReport()
    }
    
    /**
     * Loads the report by ID from the database.
     */
    private fun loadReport() {
        viewModelScope.launch {
            _state.value = _state.value.copy(isLoading = true, error = null)
            
            try {
                val report = repository.getReportById(reportId)
                if (report != null) {
                    _state.value = _state.value.copy(
                        report = report,
                        isLoading = false
                    )
                } else {
                    _state.value = _state.value.copy(
                        isLoading = false,
                        error = "Report not found"
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
}
