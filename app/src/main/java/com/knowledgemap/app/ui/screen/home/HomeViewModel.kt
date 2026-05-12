package com.knowledgemap.app.ui.screen.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.knowledgemap.app.data.local.dao.AssessmentHistoryDao
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.domain.model.Recommendation
import com.knowledgemap.app.domain.usecase.RecommendationEngine
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import javax.inject.Inject

data class HomeUiState(
    val masteryPercent: Int = 0,
    val recommendations: List<HomeRecommendationItem> = emptyList(),
    val recentActivities: List<HomeActivityItem> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

data class HomeRecommendationItem(
    val topicId: String,
    val title: String,
    val subtitle: String,
    val level: Int
)

data class HomeActivityItem(
    val title: String,
    val timeAgo: String
)

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val topicNodeDao: TopicNodeDao,
    private val assessmentHistoryDao: AssessmentHistoryDao,
    private val recommendationEngine: RecommendationEngine
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        loadHomeData()
    }

    fun loadHomeData() {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true)
            try {
                // Load topics to calculate mastery
                val topics = topicNodeDao.getAllBySubject("toan10").first()
                val total = topics.size
                val mastered = topics.count { it.skillLevel >= 3 }
                val inProgress = topics.count { it.skillLevel in 1..2 }
                val masteryPercent = if (total > 0) ((mastered + inProgress * 0.5) * 100 / total).toInt() else 0

                // Load recommendations
                val recommendations = recommendationEngine.getTopRecommendations(3)
                val homeRecommendations = recommendations.map { rec ->
                    HomeRecommendationItem(
                        topicId = rec.topic.id,
                        title = rec.topic.name,
                        subtitle = rec.reason,
                        level = rec.topic.skillLevel.coerceIn(0, 3)
                    )
                }

                // Load recent activities
                val history = assessmentHistoryDao.getRecent(10).first()
                val homeActivities = history.map { entity ->
                    val topic = topicNodeDao.getById(entity.topicId)
                    HomeActivityItem(
                        title = "Quiz: ${topic?.name ?: entity.topicId}",
                        timeAgo = formatTimeAgo(entity.timestamp)
                    )
                }

                _uiState.value = HomeUiState(
                    masteryPercent = masteryPercent,
                    recommendations = homeRecommendations,
                    recentActivities = homeActivities,
                    isLoading = false
                )
            } catch (e: Exception) {
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    error = e.message
                )
            }
        }
    }

    private fun formatTimeAgo(timestamp: Long): String {
        val diff = System.currentTimeMillis() - timestamp
        val days = diff / (1000 * 60 * 60 * 24)
        return when {
            days == 0L -> "Hôm nay"
            days == 1L -> "1 ngày trước"
            days < 7 -> "$days ngày trước"
            days < 30 -> "${days / 7} tuần trước"
            else -> "${days / 30} tháng trước"
        }
    }
}