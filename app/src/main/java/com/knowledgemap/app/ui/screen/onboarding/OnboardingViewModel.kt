package com.knowledgemap.app.ui.screen.onboarding

import androidx.lifecycle.ViewModel
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import javax.inject.Inject

data class OnboardingUiState(
    val name: String = "",
    val selectedGoals: Set<String> = emptySet(),
    val isNameError: Boolean = false,
    val canComplete: Boolean = false
)

@HiltViewModel
class OnboardingViewModel @Inject constructor() : ViewModel() {

    private val _uiState = MutableStateFlow(OnboardingUiState())
    val uiState: StateFlow<OnboardingUiState> = _uiState.asStateFlow()

    fun onNameChange(newName: String) {
        _uiState.value = _uiState.value.copy(
            name = newName,
            isNameError = newName.isBlank()
        )
        validate()
    }

    fun toggleGoal(goal: String) {
        val currentGoals = _uiState.value.selectedGoals.toMutableSet()
        if (currentGoals.contains(goal)) {
            currentGoals.remove(goal)
        } else {
            currentGoals.add(goal)
        }
        _uiState.value = _uiState.value.copy(selectedGoals = currentGoals)
        validate()
    }

    private fun validate() {
        val state = _uiState.value
        _uiState.value = state.copy(
            canComplete = state.name.isNotBlank() && state.selectedGoals.isNotEmpty()
        )
    }
}