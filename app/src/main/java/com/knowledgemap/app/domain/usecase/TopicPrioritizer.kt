package com.knowledgemap.app.domain.usecase

import com.knowledgemap.app.domain.model.Recommendation
import com.knowledgemap.app.domain.model.TopicNode
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Topic Prioritizer
 * FR-17: Priority algorithm
 *
 * Priority rules:
 * 1. Skill Level 1 (Cần ôn) là prerequisite của topic sắp học → Priority 1
 * 2. Skill Level 0 (Chưa học) đã đủ prerequisite → Priority 2
 * 3. Skill Level 2 (Đang học) chưa ôn lâu nhất → Priority 3+
 * 4. Others → Priority 100
 */
@Singleton
class TopicPrioritizer @Inject constructor(
    private val prerequisiteChecker: PrerequisiteChecker
) {
    suspend fun calculatePriority(
        topic: TopicNode,
        isPrereqOfInProgress: Boolean = false
    ): Int {
        // Priority 1: Skill Level 1 là prerequisite của topic sắp học
        if (topic.skillLevel == 1 && isPrereqOfInProgress) {
            return Recommendation.PRIORITY_PREREQ_NEED
        }

        // Priority 2: Skill Level 0 đã đủ prerequisite
        if (topic.skillLevel == 0) {
            val prereqsMet = prerequisiteChecker.areAllPrerequisitesMet(topic)
            if (prereqsMet) {
                return Recommendation.PRIORITY_READY_TO_LEARN
            }
        }

        // Priority 3: Skill Level 2 chưa ôn lâu nhất
        if (topic.skillLevel == 2) {
            val daysSinceAssessed = calculateDaysSinceAssessed(topic)
            return Recommendation.PRIORITY_NEEDS_REVIEW + (daysSinceAssessed / 7)
        }

        // Priority 4: Skill Level 1 nhưng không phải prerequisite
        if (topic.skillLevel == 1) {
            return 10
        }

        // Low priority: Skill Level 3 (Đã vững)
        return Recommendation.PRIORITY_LOW
    }

    /**
     * Generate human-readable reason for recommendation
     */
    suspend fun generateReason(topic: TopicNode): String {
        return when {
            topic.skillLevel == 0 && prerequisiteChecker.areAllPrerequisitesMet(topic) ->
                "Sẵn sàng để bắt đầu"

            topic.skillLevel == 0 && !prerequisiteChecker.areAllPrerequisitesMet(topic) -> {
                val unmet = prerequisiteChecker.getUnmetPrerequisites(topic)
                val names = unmet.take(2).map { it.name }.joinToString(", ")
                "Cần học trước: $names"
            }

            topic.skillLevel == 1 -> {
                val unmet = prerequisiteChecker.getUnmetPrerequisites(topic)
                if (unmet.isNotEmpty()) {
                    "Cần ôn lại: ${unmet.first().name}"
                } else {
                    "Cần ôn tập"
                }
            }

            topic.skillLevel == 2 -> {
                val days = calculateDaysSinceAssessed(topic)
                when {
                    days < 7 -> "Mới học gần đây"
                    days < 14 -> "Cần ôn sau 1 tuần"
                    else -> "Cần ôn tập lại"
                }
            }

            topic.skillLevel == 3 -> "Đã vững - có thể ôn tập nâng cao"

            else -> "Không xác định"
        }
    }

    private fun calculateDaysSinceAssessed(topic: TopicNode): Int {
        val lastAssessed = topic.lastAssessed ?: return 0
        val now = System.currentTimeMillis()
        val diffMillis = now - lastAssessed
        return (diffMillis / (1000 * 60 * 60 * 24)).toInt()
    }
}