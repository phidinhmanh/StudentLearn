package com.knowledgemap.app.ui.screen.recommendation

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.knowledgemap.app.domain.model.Recommendation
import com.knowledgemap.app.domain.usecase.RecommendationEngine
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class RecommendationUiState(
    val isLoading: Boolean = false,
    val recommendations: List<Recommendation> = emptyList(),
    val error: String? = null
)

@HiltViewModel
class RecommendationViewModel @Inject constructor(
    private val recommendationEngine: RecommendationEngine
) : ViewModel() {

    private val _uiState = MutableStateFlow(RecommendationUiState())
    val uiState: StateFlow<RecommendationUiState> = _uiState.asStateFlow()

    init {
        loadRecommendations()
    }

    private fun loadRecommendations() {
        _uiState.value = RecommendationUiState(isLoading = true)

        viewModelScope.launch {
            try {
                val recommendations = recommendationEngine.getTopRecommendations(3)
                _uiState.value = RecommendationUiState(
                    isLoading = false,
                    recommendations = recommendations
                )
            } catch (e: Exception) {
                _uiState.value = RecommendationUiState(
                    isLoading = false,
                    error = e.message ?: "Không thể tải gợi ý. Vui lòng thử lại."
                )
            }
        }
    }

    fun retry() {
        loadRecommendations()
    }
}
