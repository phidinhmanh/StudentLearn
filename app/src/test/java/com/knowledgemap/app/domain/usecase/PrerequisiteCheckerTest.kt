package com.knowledgemap.app.domain.usecase

import com.knowledgemap.app.data.local.dao.TopicEdgeDao
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.data.local.entity.TopicNodeEntity
import com.knowledgemap.app.domain.model.TopicNode
import io.mockk.coEvery
import io.mockk.coVerify
import io.mockk.mockk
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test

/**
 * Unit tests for PrerequisiteChecker
 * CON-D03: Kiểm tra direct và transitive prerequisite
 * CON-G03: A→B→C = A prerequisite of C
 */
class PrerequisiteCheckerTest {

    private lateinit var topicNodeDao: TopicNodeDao
    private lateinit var topicEdgeDao: TopicEdgeDao
    private lateinit var checker: PrerequisiteChecker

    @Before
    fun setup() {
        topicNodeDao = mockk(relaxed = true)
        topicEdgeDao = mockk(relaxed = true)
        checker = PrerequisiteChecker(topicNodeDao, topicEdgeDao)
    }

    // ============== getAllPrerequisiteIds() Tests ==============

    @Test
    fun `getAllPrerequisiteIds returns list from DAO`() = kotlinx.coroutines.test.runTest {
        coEvery { topicEdgeDao.getAllPrerequisiteIds("topic-B") } returns listOf("topic-A")

        val result = checker.getAllPrerequisiteIds("topic-B")

        assertEquals(listOf("topic-A"), result)
        coVerify { topicEdgeDao.getAllPrerequisiteIds("topic-B") }
    }

    @Test
    fun `getAllPrerequisiteIds returns empty list when no prerequisites`() = kotlinx.coroutines.test.runTest {
        coEvery { topicEdgeDao.getAllPrerequisiteIds("topic-A") } returns emptyList()

        val result = checker.getAllPrerequisiteIds("topic-A")

        assertTrue(result.isEmpty())
    }

    // ============== areAllPrerequisitesMet() Tests ==============

    @Test
    fun `areAllPrerequisitesMet returns true when no prerequisites`() = kotlinx.coroutines.test.runTest {
        coEvery { topicEdgeDao.getAllPrerequisiteIds(any()) } returns emptyList()

        val topic = TopicNode("topic-B", "Topic B", "Desc", 1, "Ch1", "Math", 0)

        val result = checker.areAllPrerequisitesMet(topic)

        assertTrue(result)
    }

    @Test
    fun `areAllPrerequisitesMet returns true when all prereqs at level 2 or higher`() = kotlinx.coroutines.test.runTest {
        coEvery { topicEdgeDao.getAllPrerequisiteIds("topic-C") } returns listOf("topic-A", "topic-B")
        coEvery { topicNodeDao.getById("topic-A") } returns createEntity("topic-A", skillLevel = 2)
        coEvery { topicNodeDao.getById("topic-B") } returns createEntity("topic-B", skillLevel = 3)

        val topic = TopicNode("topic-C", "Topic C", "Desc", 1, "Ch1", "Math", 0)

        val result = checker.areAllPrerequisitesMet(topic)

        assertTrue(result)
    }

    @Test
    fun `areAllPrerequisitesMet returns false when any prereq below level 2`() = kotlinx.coroutines.test.runTest {
        coEvery { topicEdgeDao.getAllPrerequisiteIds("topic-C") } returns listOf("topic-A", "topic-B")
        coEvery { topicNodeDao.getById("topic-A") } returns createEntity("topic-A", skillLevel = 3)
        coEvery { topicNodeDao.getById("topic-B") } returns createEntity("topic-B", skillLevel = 1) // Below 2

        val topic = TopicNode("topic-C", "Topic C", "Desc", 1, "Ch1", "Math", 0)

        val result = checker.areAllPrerequisitesMet(topic)

        assertFalse(result)
    }

    // ============== CON-D03: Direct and Transitive Prerequisite Tests ==============

    @Test
    fun `CON-D03 topic with transitive prerequisite not ready if direct prereq not met`() = kotlinx.coroutines.test.runTest {
        // A → B → C (A is transitive prereq of C)
        // If B is not learned (level < 2), C is not ready
        coEvery { topicEdgeDao.getAllPrerequisiteIds("topic-C") } returns listOf("topic-A", "topic-B")
        coEvery { topicNodeDao.getById("topic-A") } returns createEntity("topic-A", skillLevel = 3)
        coEvery { topicNodeDao.getById("topic-B") } returns createEntity("topic-B", skillLevel = 1) // Not learned

        val topic = TopicNode("topic-C", "Topic C", "Desc", 1, "Ch1", "Math", 0)

        val result = checker.areAllPrerequisitesMet(topic)

        assertFalse(result)
    }

    @Test
    fun `CON-G03 A is prerequisite of C through B chain`() = kotlinx.coroutines.test.runTest {
        // Graph: A → B → C
        // A is transitive prerequisite of C
        coEvery { topicEdgeDao.getAllPrerequisiteIds("topic-C") } returns listOf("topic-A", "topic-B")
        coEvery { topicNodeDao.getById("topic-A") } returns createEntity("topic-A", skillLevel = 2)
        coEvery { topicNodeDao.getById("topic-B") } returns createEntity("topic-B", skillLevel = 2)

        val topic = TopicNode("topic-C", "Topic C", "Desc", 1, "Ch1", "Math", 0)

        val result = checker.areAllPrerequisitesMet(topic)

        assertTrue(result)
    }

    // ============== isLocked() Tests ==============

    @Test
    fun `isLocked returns true when prerequisites not met`() = kotlinx.coroutines.test.runTest {
        coEvery { topicEdgeDao.getAllPrerequisiteIds(any()) } returns listOf("topic-A")
        coEvery { topicNodeDao.getById("topic-A") } returns createEntity("topic-A", skillLevel = 1)

        val topic = TopicNode("topic-B", "Topic B", "Desc", 1, "Ch1", "Math", 0)

        val result = checker.isLocked(topic)

        assertTrue(result)
    }

    @Test
    fun `isLocked returns false when prerequisites are met`() = kotlinx.coroutines.test.runTest {
        coEvery { topicEdgeDao.getAllPrerequisiteIds(any()) } returns emptyList()

        val topic = TopicNode("topic-A", "Topic A", "Desc", 1, "Ch1", "Math", 0)

        val result = checker.isLocked(topic)

        assertFalse(result)
    }

    // ============== getUnmetPrerequisites() Tests ==============

    @Test
    fun `getUnmetPrerequisites returns empty when all met`() = kotlinx.coroutines.test.runTest {
        coEvery { topicEdgeDao.getAllPrerequisiteIds(any()) } returns listOf("topic-A")
        coEvery { topicNodeDao.getById("topic-A") } returns createEntity("topic-A", skillLevel = 3)

        val topic = TopicNode("topic-B", "Topic B", "Desc", 1, "Ch1", "Math", 0)

        val result = checker.getUnmetPrerequisites(topic)

        assertTrue(result.isEmpty())
    }

    @Test
    fun `getUnmetPrerequisites returns list of unmet topics`() = kotlinx.coroutines.test.runTest {
        coEvery { topicEdgeDao.getAllPrerequisiteIds(any()) } returns listOf("topic-A", "topic-B")
        coEvery { topicNodeDao.getById("topic-A") } returns createEntity("topic-A", skillLevel = 3) // Met
        coEvery { topicNodeDao.getById("topic-B") } returns createEntity("topic-B", skillLevel = 1) // Not met

        val topic = TopicNode("topic-C", "Topic C", "Desc", 1, "Ch1", "Math", 0)

        val result = checker.getUnmetPrerequisites(topic)

        assertEquals(1, result.size)
        assertEquals("topic-B", result.first().id)
    }

    @Test
    fun `getUnmetPrerequisites handles null prerequisite`() = kotlinx.coroutines.test.runTest {
        coEvery { topicEdgeDao.getAllPrerequisiteIds(any()) } returns listOf("topic-A")
        coEvery { topicNodeDao.getById("topic-A") } returns null

        val topic = TopicNode("topic-B", "Topic B", "Desc", 1, "Ch1", "Math", 0)

        val result = checker.getUnmetPrerequisites(topic)

        assertTrue(result.isEmpty())
    }

    // ============== Helper Methods ==============

    private fun createEntity(
        id: String,
        name: String = "Topic $id",
        skillLevel: Int = 0
    ): TopicNodeEntity {
        return TopicNodeEntity(
            id = id,
            name = name,
            desc = "Description",
            difficulty = 1,
            chapter = "Ch1",
            subject = "Math",
            skillLevel = skillLevel,
            lastAssessed = null
        )
    }
}