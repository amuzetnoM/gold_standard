package com.goldstandard.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.goldstandard.data.repository.GoldRepository
import com.goldstandard.model.Report
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * UI state for the Reports screen.
 */
data class ReportsState(
    val isLoading: Boolean = false,
    val error: String? = null
)

/**
 * ViewModel for the Reports screen.
 * Manages local report data.
 */
@HiltViewModel
class ReportsViewModel @Inject constructor(
    private val repository: GoldRepository
) : ViewModel() {
    
    private val _state = MutableStateFlow(ReportsState())
    val state: StateFlow<ReportsState> = _state.asStateFlow()
    
    /**
     * Flow of all reports from the database.
     */
    val reports: StateFlow<List<Report>> = repository.getReports()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
    
    /**
     * Saves a new report to the database.
     */
    fun saveReport(title: String, content: String) {
        viewModelScope.launch {
            val report = Report(
                title = title,
                date = System.currentTimeMillis(),
                content = content
            )
            repository.saveReport(report)
        }
    }
    
    /**
     * Deletes a report by ID.
     */
    fun deleteReport(id: Int) {
        viewModelScope.launch {
            repository.deleteReport(id)
        }
    }
}
