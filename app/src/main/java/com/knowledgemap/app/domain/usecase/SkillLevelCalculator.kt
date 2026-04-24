package com.knowledgemap.app.domain.usecase

import javax.inject.Inject
import javax.inject.Singleton

/**
 * Skill Level Calculator
 * FR-13: Scoring → Skill Level mapping
 *
 * Mapping:
 * - 0-1 correct → L1 (Cần ôn)
 * - 2-3 correct → L2 (Đang học)
 * - 4-5 correct → L3 (Đã vững)
 */
@Singleton
class SkillLevelCalculator @Inject constructor() {

    /**
     * Calculate new skill level from correct answers
     * @param correctAnswers Number of correct answers (0-5)
     * @return New skill level (1, 2, or 3)
     */
    fun calculate(correctAnswers: Int): Int {
        return when (correctAnswers) {
            in 0..1 -> 1 // Cần ôn
            in 2..3 -> 2 // Đang học
            in 4..5 -> 3 // Đã vững
            else -> 1 // Default to "Cần ôn"
        }
    }

    /**
     * Calculate skill level change (delta)
     * @param correctAnswers Number of correct answers
     * @param currentLevel Current skill level (0-3)
     * @return Skill level after assessment
     */
    fun calculateAfterAssessment(correctAnswers: Int, currentLevel: Int): Int {
        val newLevel = calculate(correctAnswers)
        return maxOf(newLevel, currentLevel) // Never decrease skill level from assessment
    }

    /**
     * Get skill level label (Vietnamese)
     */
    fun getLabel(level: Int): String {
        return when (level) {
            0 -> "Chưa học"
            1 -> "Cần ôn"
            2 -> "Đang học"
            3 -> "Đã vững"
            else -> "Chưa học"
        }
    }

    /**
     * Get description for recommendation
     */
    fun getRecommendationReason(score: Int, total: Int): String {
        val percentage = (score.toFloat() / total) * 100
        return when {
            percentage >= 80 -> "Kết quả tốt - củng cố kiến thức"
            percentage >= 50 -> "Cần ôn tập thêm"
            else -> "Cần học lại từ đầu"
        }
    }
}