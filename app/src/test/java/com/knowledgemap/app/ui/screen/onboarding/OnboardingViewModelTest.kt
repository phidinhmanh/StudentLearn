package com.knowledgemap.app.ui.screen.onboarding

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

@OptIn(ExperimentalCoroutinesApi::class)
class OnboardingViewModelTest {

    private val testDispatcher = StandardTestDispatcher()

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    private val viewModel = OnboardingViewModel()

    @Test
    fun `initial state has empty name and no goals`() {
        val state = viewModel.uiState.value
        assertEquals("", state.name)
        assertTrue(state.selectedGoals.isEmpty())
        assertFalse(state.canComplete)
        assertFalse(state.isNameError)
    }

    @Test
    fun `onNameChange with blank name sets error`() {
        viewModel.onNameChange("")
        val state1 = viewModel.uiState.value
        assertTrue(state1.isNameError)
        assertFalse(state1.canComplete)

        viewModel.onNameChange("  ")
        val state2 = viewModel.uiState.value
        assertTrue(state2.isNameError)
        assertFalse(state2.canComplete)
    }

    @Test
    fun `onNameChange with valid name clears error`() {
        viewModel.onNameChange("Minh")
        val state = viewModel.uiState.value
        assertEquals("Minh", state.name)
        assertFalse(state.isNameError)
    }

    @Test
    fun `toggleGoal adds and removes goal from selection`() {
        viewModel.toggleGoal("Lấy gốc kiến thức")
        assertTrue(viewModel.uiState.value.selectedGoals.contains("Lấy gốc kiến thức"))

        viewModel.toggleGoal("Lấy gốc kiến thức")
        assertFalse(viewModel.uiState.value.selectedGoals.contains("Lấy gốc kiến thức"))
    }

    @Test
    fun `canComplete true only when name not blank and at least one goal selected`() {
        assertFalse(viewModel.uiState.value.canComplete)

        viewModel.onNameChange("Minh")
        assertFalse(viewModel.uiState.value.canComplete)

        viewModel.toggleGoal("Lấy gốc")
        assertTrue(viewModel.uiState.value.canComplete)
    }

    @Test
    fun `canComplete false when name cleared`() {
        viewModel.onNameChange("Minh")
        viewModel.toggleGoal("Lấy gốc")
        assertTrue(viewModel.uiState.value.canComplete)

        viewModel.onNameChange("")
        val state = viewModel.uiState.value
        assertFalse(state.canComplete)
        assertTrue(state.isNameError)
    }
}