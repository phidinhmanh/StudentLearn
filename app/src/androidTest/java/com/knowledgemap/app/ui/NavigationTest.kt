package com.knowledgemap.app.ui

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import com.knowledgemap.app.ui.MainActivity
import com.knowledgemap.app.ui.navigation.Screen
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.Rule
import org.junit.Test

/**
 * Integration tests for Navigation and User Journeys
 * Verifies core flows: Onboarding -> Home -> Knowledge Map -> Assessment
 */
@HiltAndroidTest
class NavigationTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun onboarding_to_home_navigation() {
        composeTestRule.mainClock.autoAdvance = true
        // Start at Onboarding
        composeTestRule.onNodeWithText("EMBER", useUnmergedTree = true).assertIsDisplayed()

        // Skip through intro (if needed) or just click Start
        composeTestRule.onNodeWithText("BẮT ĐẦU NGAY").performClick()

        // Goal selection
        composeTestRule.onNodeWithText("Mục tiêu của bạn là gì?").assertIsDisplayed()
        composeTestRule.onNodeWithText("Lấy gốc kiến thức").performClick()
        composeTestRule.onNodeWithText("Hoàn tất").performClick()

        // Verify we are at Home / Knowledge Map (depending on startDestination logic)
        // Since NavGraph navigates to BottomBarScreen.Home.route
        composeTestRule.onNodeWithTag("bottom_nav").assertIsDisplayed()
    }

    @Test
    fun knowledgeMap_to_assessment_navigation() {
        // Assume we start at Home/Graph
        // Navigate to Knowledge Map via Bottom Nav if not there
        composeTestRule.onNodeWithTag("nav_item_graph").performClick()

        // Find a topic and click it
        // Note: Topic names depend on database seed
        // We look for a node and click
        composeTestRule.onAllNodesWithText("Mệnh đề").onFirst().performClick()

        // Verify Assessment screen opened
        composeTestRule.onNodeWithText("Bắt đầu đánh giá").assertIsDisplayed()
    }

    @Test
    fun assessment_back_returns_to_previous_screen() {
        // Navigate to Assessment
        composeTestRule.onNodeWithTag("nav_item_graph").performClick()
        composeTestRule.onAllNodesWithText("Mệnh đề").onFirst().performClick()

        // Verify Assessment screen
        composeTestRule.onNodeWithContentDescription("Back").performClick()

        // Verify we are back at Knowledge Map
        composeTestRule.onNodeWithText("Tiến độ tổng thể").assertIsDisplayed()
    }
}