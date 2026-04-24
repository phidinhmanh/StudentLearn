package com.knowledgemap.app.ui.screen.knowledge

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import com.knowledgemap.app.domain.model.TopicNode
import com.knowledgemap.app.ui.theme.KnowledgeMapTheme
import org.junit.Rule
import org.junit.Test

class KnowledgeMapScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    private val mockTopics = listOf(
        TopicNode("1", "Mệnh đề", "Desc", 1, "Chương 1", "toan10", 3, null),
        TopicNode("2", "Tập hợp", "Desc", 2, "Chương 1", "toan10", 1, null),
        TopicNode("3", "Bất phương trình", "Desc", 3, "Chương 2", "toan10", 0, null)
    )

    private val mockUiState = KnowledgeMapUiState(
        topics = mockTopics,
        completedCount = 1,
        totalCount = 3,
        progressPercent = 33,
        lockedTopicIds = setOf("3")
    )

    @Test
    fun knowledgeMap_displaysProgressAndTopics() {
        composeTestRule.setContent {
            KnowledgeMapTheme {
                KnowledgeMapContent(
                    uiState = mockUiState,
                    onTopicClick = {},
                    onRecommendationsClick = {}
                )
            }
        }

        // Verify Progress Card
        composeTestRule.onNodeWithText("Tiến độ tổng thể").assertIsDisplayed()
        composeTestRule.onNodeWithText("33%").assertIsDisplayed()
        composeTestRule.onNodeWithText("Hoàn thành: 1/3 bài học").assertIsDisplayed()

        // Verify Chapters and Topics
        composeTestRule.onNodeWithText("Chương 1").assertIsDisplayed()
        composeTestRule.onNodeWithText("Mệnh đề").assertIsDisplayed()
        composeTestRule.onNodeWithText("Tập hợp").assertIsDisplayed()
        composeTestRule.onNodeWithText("Chương 2").assertIsDisplayed()
        composeTestRule.onNodeWithText("Bất phương trình").assertIsDisplayed()
    }

    @Test
    fun knowledgeMap_filterWorks() {
        composeTestRule.setContent {
            KnowledgeMapTheme {
                KnowledgeMapContent(
                    uiState = mockUiState,
                    onTopicClick = {},
                    onRecommendationsClick = {}
                )
            }
        }

        // Click on L3 filter
        composeTestRule.onNodeWithText("L3").performClick()

        // Should only show "Mệnh đề" (skillLevel 3)
        composeTestRule.onNodeWithText("Mệnh đề").assertIsDisplayed()
        composeTestRule.onNodeWithText("Tập hợp").assertDoesNotExist()
        composeTestRule.onNodeWithText("Bất phương trình").assertDoesNotExist()

        // Click back to "Tất cả"
        composeTestRule.onNodeWithText("Tất cả").performClick()
        composeTestRule.onNodeWithText("Tập hợp").assertIsDisplayed()
    }

    @Test
    fun knowledgeMap_clickTopic_triggersCallback() {
        var clickedTopicId: String? = null
        composeTestRule.setContent {
            KnowledgeMapTheme {
                KnowledgeMapContent(
                    uiState = mockUiState,
                    onTopicClick = { clickedTopicId = it },
                    onRecommendationsClick = {}
                )
            }
        }

        composeTestRule.onNodeWithText("Mệnh đề").performClick()
        assert(clickedTopicId == "1")
    }
}
