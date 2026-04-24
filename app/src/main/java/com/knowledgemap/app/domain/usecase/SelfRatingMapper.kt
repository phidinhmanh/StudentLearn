package com.knowledgemap.app.domain.usecase

import javax.inject.Inject
import javax.inject.Singleton

/**
 * Self Rating Mapper
 * FR-22: Self-rating → Skill Level mapping
 *
 * Mapping:
 * - Hiểu rõ (2) → +1 bậc (không quá 3)
 * - Cần ôn lại (1) → giữ nguyên
 * - Chưa hiểu (0) → -1 bậc (không dưới 0)
 */
@Singleton
class SelfRatingMapper @Inject constructor() {

    enum class SelfRating(val value: Int) {
        CHUA_HIEU(0),
        CAN_ON(1),
        HIEU_RO(2);

        companion object {
            fun fromValue(value: Int): SelfRating = when (value) {
                0 -> CHUA_HIEU
                1 -> CAN_ON
                2 -> HIEU_RO
                else -> CAN_ON
            }
        }
    }

    /**
     * Apply self-rating to current skill level
     * @param currentLevel Current skill level (0-3)
     * @param rating Self-rating value (0-2)
     * @return New skill level after applying rating
     */
    fun applyRating(currentLevel: Int, rating: Int): Int {
        return applyRating(currentLevel, SelfRating.fromValue(rating))
    }

    fun applyRating(currentLevel: Int, rating: SelfRating): Int {
        return when (rating) {
            SelfRating.HIEU_RO -> minOf(currentLevel + 1, 3)
            SelfRating.CAN_ON -> currentLevel
            SelfRating.CHUA_HIEU -> maxOf(currentLevel - 1, 0)
        }
    }

    /**
     * Get label for rating value
     */
    fun getLabel(rating: Int): String {
        return getLabel(SelfRating.fromValue(rating))
    }

    fun getLabel(rating: SelfRating): String {
        return when (rating) {
            SelfRating.CHUA_HIEU -> "Chưa hiểu"
            SelfRating.CAN_ON -> "Cần ôn lại"
            SelfRating.HIEU_RO -> "Hiểu rõ"
        }
    }

    /**
     * Get description of what will happen to skill level
     */
    fun getDescription(currentLevel: Int, rating: Int): String {
        val newLevel = applyRating(currentLevel, rating)
        val delta = newLevel - currentLevel

        return when {
            delta > 0 -> "Skill level sẽ tăng từ $currentLevel lên $newLevel"
            delta < 0 -> "Skill level sẽ giảm từ $currentLevel xuống $newLevel"
            else -> "Skill level được giữ nguyên ở $currentLevel"
        }
    }
}