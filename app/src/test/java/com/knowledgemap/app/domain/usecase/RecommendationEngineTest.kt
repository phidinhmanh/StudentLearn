package com.knowledgemap.app.domain.usecase

import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.data.local.entity.TopicNodeEntity
import com.knowledgemap.app.domain.model.TopicNode
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.*

class RecommendationEngineTest {

    @Mock private lateinit var topicNodeDao: TopicNodeDao
    @Mock private lateinit var prerequisiteChecker: PrerequisiteChecker
    @Mock private lateinit var topicPrioritizer: TopicPrioritizer

    private lateinit var recommendationEngine: RecommendationEngine

    private val testTopics = listOf(
        TopicNodeEntity("1", "Topic 1", "", 1, "C1", "toan10", 1, 123L), // Gap
        TopicNodeEntity("2", "Topic 2", "", 1, "C1", "toan10", 2, 123L), // Learning
        TopicNodeEntity("3", "Topic 3", "", 1, "C1", "toan10", 3, 123L), // Mastered (should skip)
        TopicNodeEntity("4", "Topic 4", "", 1, "C1", "toan10", 0, null)  // New (should skip in getTopRec)
    )

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        recommendationEngine = RecommendationEngine(
            topicNodeDao = topicNodeDao,
            prerequisiteChecker = prerequisiteChecker,
            topicPrioritizer = topicPrioritizer
        )
    }

    @Test
    fun `getTopRecommendations filters out mastered and new topics`() = runTest {
        whenever(topicNodeDao.getAllBySubject("toan10")).thenReturn(flowOf(testTopics))
        whenever(topicPrioritizer.calculatePriority(any<TopicNode>(), any())).thenReturn(1)
        whenever(topicPrioritizer.generateReason(any<TopicNode>())).thenReturn("Reason")

        val result = recommendationEngine.getTopRecommendations(limit = 10)

        assertEquals(2, result.size)
        assertTrue(result.any { it.topic.id == "1" })
        assertTrue(result.any { it.topic.id == "2" })
    }

    @Test
    fun `getTopRecommendations limits results to N`() = runTest {
        whenever(topicNodeDao.getAllBySubject("toan10")).thenReturn(flowOf(testTopics))
        whenever(topicPrioritizer.calculatePriority(any<TopicNode>(), any())).thenReturn(1)
        whenever(topicPrioritizer.generateReason(any<TopicNode>())).thenReturn("Reason")

        val result = recommendationEngine.getTopRecommendations(limit = 1)
        assertEquals(1, result.size)
    }

    @Test
    fun `getNextTopics returns prerequisites if topic is locked`() = runTest {
        val targetTopic = TopicNodeEntity("4", "Locked Topic", "", 1, "C1", "toan10", 0, null)
        val prereq = TopicNode("1", "Prereq", "", 1, "C1", "toan10", 1, null)

        whenever(topicNodeDao.getById("4")).thenReturn(targetTopic)
        whenever(prerequisiteChecker.isLocked(any<TopicNode>())).thenReturn(true)
        whenever(prerequisiteChecker.getUnmetPrerequisites(any<TopicNode>())).thenReturn(listOf(prereq))
        whenever(topicPrioritizer.calculatePriority(any<TopicNode>(), any())).thenReturn(1)

        val result = recommendationEngine.getNextTopics("4")

        assertEquals(1, result.size)
        assertEquals("1", result[0].topic.id)
    }

    @Test
    fun `getNextTopics returns itself if topic is ready to learn`() = runTest {
        val targetTopic = TopicNodeEntity("4", "Ready Topic", "", 1, "C1", "toan10", 0, null)

        whenever(topicNodeDao.getById("4")).thenReturn(targetTopic)
        whenever(prerequisiteChecker.isLocked(any<TopicNode>())).thenReturn(false)

        val result = recommendationEngine.getNextTopics("4")

        assertEquals(1, result.size)
        assertEquals("4", result[0].topic.id)
        assertEquals("Sẵn sàng để học", result[0].reason)
    }
}