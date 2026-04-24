package com.knowledgemap.app.ui.screen.session

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.domain.usecase.SelfRatingMapper
import com.knowledgemap.app.domain.usecase.SessionLoggerUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class SessionLoggerUiState(
    val topicId: String = "",
    val topicName: String = "",
    val currentSkill: Int = 0,
    val selectedRating: Int? = null,
    val isSaving: Boolean = false
)

@HiltViewModel
class SessionLoggerViewModel @Inject constructor(
    private val sessionLoggerUseCase: SessionLoggerUseCase,
    private val topicNodeDao: TopicNodeDao,
    private val selfRatingMapper: SelfRatingMapper
) : ViewModel() {

    private val _uiState = MutableStateFlow(SessionLoggerUiState())
    val uiState: StateFlow<SessionLoggerUiState> = _uiState.asStateFlow()

    private var sessionId: Long = 0

    fun loadTopic(topicId: String) {
        viewModelScope.launch {
            val topic = topicNodeDao.getById(topicId)
            if (topic != null) {
                _uiState.value = SessionLoggerUiState(
                    topicId = topicId,
                    topicName = topic.name,
                    currentSkill = topic.skillLevel
                )
                sessionId = sessionLoggerUseCase.startSession(topicId)
            }
        }
    }

    fun selectRating(rating: Int) {
        _uiState.value = _uiState.value.copy(selectedRating = rating)
    }

    fun getNewSkillLevel(): Int {
        val current = _uiState.value
        return if (current.selectedRating != null) {
            selfRatingMapper.applyRating(current.currentSkill, current.selectedRating)
        } else {
            current.currentSkill
        }
    }

    fun saveSession() {
        val current = _uiState.value
        if (current.selectedRating == null) return

        viewModelScope.launch {
            _uiState.value = current.copy(isSaving = true)
            sessionLoggerUseCase.endSession(sessionId, current.selectedRating)
        }
    }
}