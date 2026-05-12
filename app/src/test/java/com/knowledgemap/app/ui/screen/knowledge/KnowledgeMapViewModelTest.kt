package com.knowledgemap.app.ui.screen.knowledge

import app.cash.turbine.test
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.data.local.entity.TopicNodeEntity
import com.knowledgemap.app.domain.model.TopicNode
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.TestScope
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import kotlinx.coroutines.test.runCurrent
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.MockitoAnnotations
import org.mockito.kotlin.*

@OptIn(ExperimentalCoroutinesApi::class)
class KnowledgeMapViewModelTest {

    @Mock private lateinit var topicNodeDao: TopicNodeDao
    private val testDispatcher = StandardTestDispatcher()

    private val testEntities = listOf(
        TopicNodeEntity("1", "Mệnh đề", "Desc", 1, "Chương 1", "toan10", 3, 123L),  // Mastered
        TopicNodeEntity("2", "Tập hợp", "Desc", 1, "Chương 1", "toan10", 1, 123L),  // Gap
        TopicNodeEntity("3", "Bất phương trình", "Desc", 2, "Chương 2", "toan10", 0, null)  // Locked
    )

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        Dispatchers.setMain(testDispatcher)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `initial load emits topics with correct progress`() = runTest {
        whenever(topicNodeDao.getAllBySubject("toan10")).thenReturn(flowOf(testEntities))
        val viewModel = KnowledgeMapViewModel(topicNodeDao)

        viewModel.uiState.test {
            advanceUntilIdle()
            val state = expectMostRecentItem()
            assertEquals(3, state.topics.size)
            assertEquals(1, state.completedCount)
            assertEquals(3, state.totalCount)
            assertEquals(33, state.progressPercent)
            assertEquals(setOf("3"), state.lockedTopicIds)
        }
    }

    @Test
    fun `topics are mapped correctly to domain model`() = runTest {
        whenever(topicNodeDao.getAllBySubject("toan10")).thenReturn(flowOf(testEntities))
        val viewModel = KnowledgeMapViewModel(topicNodeDao)

        viewModel.uiState.test {
            advanceUntilIdle()
            val topics = expectMostRecentItem().topics
            assertEquals("Mệnh đề", topics[0].name)
            assertEquals(3, topics[0].skillLevel)
            assertEquals("Tập hợp", topics[1].name)
            assertEquals(1, topics[1].skillLevel)
            assertEquals("Bất phương trình", topics[2].name)
            assertEquals(0, topics[2].skillLevel)
        }
    }

    @Test
    fun `progress is 0 when no topics`() = runTest {
        whenever(topicNodeDao.getAllBySubject("toan10")).thenReturn(flowOf(emptyList()))
        val viewModel = KnowledgeMapViewModel(topicNodeDao)

        viewModel.uiState.test {
            advanceUntilIdle()
            val state = expectMostRecentItem()
            assertEquals(0, state.completedCount)
            assertEquals(0, state.totalCount)
            assertEquals(0, state.progressPercent)
            assertTrue(state.lockedTopicIds.isEmpty())
        }
    }

    @Test
    fun `lockedTopicIds contains all topics with skillLevel 0`() = runTest {
        val allLocked = listOf(
            TopicNodeEntity("a", "T1", "", 1, "C1", "toan10", 0, null),
            TopicNodeEntity("b", "T2", "", 1, "C1", "toan10", 0, null),
            TopicNodeEntity("c", "T3", "", 1, "C1", "toan10", 1, null)
        )
        whenever(topicNodeDao.getAllBySubject("toan10")).thenReturn(flowOf(allLocked))
        val viewModel = KnowledgeMapViewModel(topicNodeDao)

        viewModel.uiState.test {
            advanceUntilIdle()
            val state = expectMostRecentItem()
            assertEquals(setOf("a", "b"), state.lockedTopicIds)
        }
    }
}