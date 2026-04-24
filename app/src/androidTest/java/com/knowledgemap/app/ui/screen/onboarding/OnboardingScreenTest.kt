package com.knowledgemap.app.ui.screen.onboarding

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import com.knowledgemap.app.ui.theme.KnowledgeMapTheme
import org.junit.Rule
import org.junit.Test

class OnboardingScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun onboardingFlow_displaysIntroThenGoalSelection() {
        var completed = false

        composeTestRule.setContent {
            KnowledgeMapTheme {
                OnboardingScreen(onComplete = { completed = true })
            }
        }

        // 1. Verify Intro Screen
        composeTestRule.onNodeWithText("StudentLearn").assertIsDisplayed()
        composeTestRule.onNodeWithText("Học Toán lớp 10 cá nhân hóa").assertIsDisplayed()
        composeTestRule.onNodeWithText("Bắt đầu ngay").assertIsDisplayed()

        // 2. Click Next to Goal Selection
        composeTestRule.onNodeWithText("Bắt đầu ngay").performClick()

        // 3. Verify Goal Selection Screen
        composeTestRule.onNodeWithText("Mục tiêu của bạn là gì?").assertIsDisplayed()
        composeTestRule.onNodeWithText("Hoàn tất").assertIsNotEnabled()

        // 4. Select a goal
        composeTestRule.onNodeWithText("Lấy gốc kiến thức").performClick()

        // 5. Verify Finish button is enabled
        composeTestRule.onNodeWithText("Hoàn tất").assertIsEnabled()

        // 6. Click Finish and verify callback
        composeTestRule.onNodeWithText("Hoàn tất").performClick()
        assert(completed)
    }

    @Test
    fun goalSelection_multipleGoalsToggle() {
        composeTestRule.setContent {
            KnowledgeMapTheme {
                OnboardingScreen(onComplete = {})
            }
        }

        // Navigate to Goal Selection
        composeTestRule.onNodeWithText("Bắt đầu ngay").performClick()

        // Select multiple
        composeTestRule.onNodeWithText("Lấy gốc kiến thức").performClick()
        composeTestRule.onNodeWithText("Ôn thi học kỳ").performClick()

        // Deselect one
        composeTestRule.onNodeWithText("Lấy gốc kiến thức").performClick()

        // Verify still enabled because "Ôn thi học kỳ" is still selected
        composeTestRule.onNodeWithText("Hoàn tất").assertIsEnabled()

        // Deselect last one
        composeTestRule.onNodeWithText("Ôn thi học kỳ").performClick()
        composeTestRule.onNodeWithText("Hoàn tất").assertIsNotEnabled()
    }
}
