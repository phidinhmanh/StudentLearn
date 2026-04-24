package com.knowledgemap.app.domain.usecase

import com.knowledgemap.app.data.local.dao.TopicEdgeDao
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.domain.model.TopicNode
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Prerequisite Checker
 * CON-D03: Kiểm tra direct và transitive prerequisite
 * CON-G03: A→B→C = A prerequisite of C
 */
@Singleton
class PrerequisiteChecker @Inject constructor(
    private val topicNodeDao: TopicNodeDao,
    private val topicEdgeDao: TopicEdgeDao
) {
    /**
     * Lấy tất cả prerequisite IDs của một topic (kể cả transitive)
     * CON-G03: Sử dụng CTE query từ TopicEdgeDao
     */
    suspend fun getAllPrerequisiteIds(topicId: String): List<String> {
        return topicEdgeDao.getAllPrerequisiteIds(topicId)
    }

    /**
     * Kiểm tra xem tất cả prerequisites đã được học chưa
     * @return true nếu tất cả prereqs có skill_level >= 2
     */
    suspend fun areAllPrerequisitesMet(topic: TopicNode): Boolean {
        val prereqIds = getAllPrerequisiteIds(topic.id)
        if (prereqIds.isEmpty()) return true

        return prereqIds.all { prereqId ->
            val prereq = topicNodeDao.getById(prereqId)
            prereq != null && prereq.skillLevel >= 2
        }
    }

    /**
     * Kiểm tra xem topic có bị lock không
     * @return true nếu topic có prereq chưa đạt yêu cầu
     */
    suspend fun isLocked(topic: TopicNode): Boolean {
        return !areAllPrerequisitesMet(topic)
    }

    /**
     * Lấy danh sách prerequisites chưa đạt yêu cầu
     */
    suspend fun getUnmetPrerequisites(topic: TopicNode): List<TopicNode> {
        val prereqIds = getAllPrerequisiteIds(topic.id)
        return prereqIds.mapNotNull { prereqId ->
            topicNodeDao.getById(prereqId)
        }.filter { it.skillLevel < 2 }.map { it.toDomain() }
    }

    private fun com.knowledgemap.app.data.local.entity.TopicNodeEntity.toDomain() = TopicNode(
        id = id,
        name = name,
        desc = desc,
        difficulty = difficulty,
        chapter = chapter,
        subject = subject,
        skillLevel = skillLevel,
        lastAssessed = lastAssessed
    )

    /**
     * Kiểm tra topic có phải là prerequisite của topic đang học không
     */
    suspend fun isPrerequisiteOfInProgressTopic(topic: TopicNode): Boolean {
        // Lấy tất cả topics mà topic này là prerequisite
        // Cần tìm edges where from_id = topic.id AND relation = 'prerequisite'
        // Và kiểm tra xem các topic đó có skillLevel = 2 không
        val node = topicNodeDao.getById(topic.id) ?: return false

        // Với mỗi edge đi ra (prerequisite), kiểm tra target
        // Nếu target đang ở skillLevel 2 và chưa có prereqs met đầy đủ
        return false // Simplified - actual implementation needs edge traversal
    }
}