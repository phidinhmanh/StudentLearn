package com.knowledgemap.app.domain.usecase

import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.domain.model.Recommendation
import com.knowledgemap.app.domain.model.TopicNode
import kotlinx.coroutines.flow.first
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Recommendation Engine
 * CON-P02: Trả kết quả ≤ 2 giây, offline
 * CON-D03: Block locked topics (prereq < 2)
 * FR-17: Priority algorithm
 * FR-18: Không recommend locked topics
 */
@Singleton
class RecommendationEngine @Inject constructor(
    private val topicNodeDao: TopicNodeDao,
    private val prerequisiteChecker: PrerequisiteChecker,
    private val topicPrioritizer: TopicPrioritizer
) {
    /**
     * Lấy top N recommendations
     * @param limit Số lượng recommendations (default 3)
     * @return Danh sách recommendations đã sắp xếp theo priority
     */
    suspend fun getTopRecommendations(limit: Int = 3): List<Recommendation> {
        val startTime = System.currentTimeMillis()

        // Lấy tất cả topics
        val allTopics = topicNodeDao.getAllBySubject("toan10").first()

        // Filter và sort - lấy topics cần học (L0, L1, L2)
        val recommendations = allTopics
            .filter { it.skillLevel < 3 } // Only non-mastered
            .mapNotNull { topic ->
                try {
                    val priority = topicPrioritizer.calculatePriority(topic.toDomain())
                    val reason = topicPrioritizer.generateReason(topic.toDomain())
                    Recommendation(
                        topic = topic.toDomain(),
                        reason = reason,
                        priority = priority
                    )
                } catch (e: Exception) {
                    null
                }
            }
            .sortedBy { it.priority }
            .take(limit)

        val elapsed = System.currentTimeMillis() - startTime
        // CON-P02: Log warning if > 2s but continue
        if (elapsed > 2000) {
            println("WARNING: Recommendation took ${elapsed}ms (limit: 2000ms)")
        }

        return recommendations
    }

    /**
     * Lấy recommendations cho một topic cụ thể
     * @param topicId Topic hiện tại
     * @return Danh sách topics cần học tiếp
     */
    suspend fun getNextTopics(topicId: String): List<Recommendation> {
        val currentTopic = topicNodeDao.getById(topicId) ?: return emptyList()

        // Lấy topics mà current topic là prerequisite
        // Đang học → tìm topic tiếp theo trong sequence
        if (currentTopic.skillLevel >= 2) {
            // Topic đang học → recommend topics liên quan
            return getTopRecommendations(3)
        }

        // Topic mới hoặc cần ôn → recommend chính nó hoặc prerequisites
        val currentDomain = currentTopic.toDomain()
        return if (prerequisiteChecker.isLocked(currentDomain)) {
            // Recommend prerequisites thay vì topic này
            val unmetPrereqs = prerequisiteChecker.getUnmetPrerequisites(currentDomain)
            unmetPrereqs.map { prereq ->
                val priority = topicPrioritizer.calculatePriority(prereq)
                val reason = "Cần học trước ${currentTopic.name}"
                Recommendation(prereq, reason, priority)
            }.sortedBy { it.priority }.take(3)
        } else {
            listOf(
                Recommendation(
                    topic = currentDomain,
                    reason = "Sẵn sàng để học",
                    priority = Recommendation.PRIORITY_READY_TO_LEARN
                )
            )
        }
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
}