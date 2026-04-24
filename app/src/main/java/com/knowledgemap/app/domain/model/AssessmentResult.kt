package com.knowledgemap.app.domain.model

/**
 * Domain model cho QuizQuestion
 * CON-A05: Mỗi câu phải có đủ 4 fields: q, opts, correct, explain
 */
data class QuizQuestion(
    val question: String,
    val options: List<String>, // 4 options
    val correctIndex: Int, // 0-3
    val explanation: String
) {
    init {
        require(options.size == 4) { "Must have exactly 4 options" }
        require(correctIndex in 0..3) { "Correct index must be 0-3" }
    }
}

/**
 * Domain model cho AssessmentResult
 */
data class AssessmentResult(
    val topicId: String,
    val score: Int,
    val totalQuestions: Int,
    val skillBefore: Int,
    val skillAfter: Int,
    val timestamp: Long,
    val source: AssessmentSource
) {
    val correctPercentage: Float get() = (score.toFloat() / totalQuestions) * 100
}

/** Assessment source */
enum class AssessmentSource {
    GEMINI,
    SELF_REPORT;

    companion object {
        fun fromString(value: String): AssessmentSource = when (value.lowercase()) {
            "gemini" -> GEMINI
            "self_report" -> SELF_REPORT
            else -> GEMINI
        }
    }

    fun toDbString(): String = when (this) {
        GEMINI -> "gemini"
        SELF_REPORT -> "self_report"
    }
}