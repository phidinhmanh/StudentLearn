package com.knowledgemap.app.ui.screen.assessment

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.knowledgemap.app.domain.model.QuizQuestion
import com.knowledgemap.app.domain.usecase.AssessmentUseCase
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class AssessmentUiState(
    val topicId: String = "",
    val topicName: String = "",
    val isLoading: Boolean = false,
    val questions: List<QuizQuestion> = emptyList(),
    val currentIndex: Int = 0,
    val selectedAnswer: Int? = null,
    val showExplanation: Boolean = false,
    val answers: Map<Int, Int> = emptyMap(),
    val showResults: Boolean = false,
    val score: Int = 0,
    val totalQuestions: Int = 0,
    val skillBefore: Int = 0,
    val skillAfter: Int = 0,
    val error: String? = null
)

@HiltViewModel
class AssessmentViewModel @Inject constructor(
    private val assessmentUseCase: AssessmentUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow(AssessmentUiState())
    val uiState: StateFlow<AssessmentUiState> = _uiState.asStateFlow()

    private var session: AssessmentUseCase.QuizSession? = null

    fun loadQuiz(topicId: String) {
        _uiState.value = AssessmentUiState(topicId = topicId, isLoading = true)

        viewModelScope.launch {
            val result = assessmentUseCase.generateQuiz(topicId)
            result.fold(
                onSuccess = { quizSession ->
                    session = quizSession
                    _uiState.value = AssessmentUiState(
                        topicId = topicId,
                        topicName = quizSession.topicName,
                        questions = quizSession.questions,
                        totalQuestions = quizSession.questions.size
                    )
                },
                onFailure = { e ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        error = e.message ?: "Không thể tạo quiz"
                    )
                }
            )
        }
    }

    fun selectAnswer(answerIndex: Int) {
        val current = _uiState.value
        if (current.selectedAnswer != null) return

        _uiState.value = current.copy(
            selectedAnswer = answerIndex,
            showExplanation = true
        )
    }

    fun nextQuestion() {
        val current = _uiState.value
        val session = session ?: return

        val newAnswers = current.answers + (current.currentIndex to (current.selectedAnswer ?: -1))
        val isLastQuestion = current.currentIndex >= current.questions.size - 1

        if (isLastQuestion) {
            viewModelScope.launch {
                val finalSession = session.copy(
                    answers = newAnswers.filterValues { it >= 0 }
                )
                val result = assessmentUseCase.submitQuiz(finalSession)

                _uiState.value = current.copy(
                    showResults = true,
                    score = result.score,
                    skillBefore = result.skillBefore,
                    skillAfter = result.skillAfter,
                    answers = result.answers
                )
            }
        } else {
            _uiState.value = current.copy(
                currentIndex = current.currentIndex + 1,
                selectedAnswer = null,
                showExplanation = false,
                answers = newAnswers
            )
        }
    }
}
