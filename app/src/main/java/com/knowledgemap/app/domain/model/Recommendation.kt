package com.knowledgemap.app.domain.model

/**
 * Domain model cho Recommendation
 * FR-17: Priority algorithm
 */
data class Recommendation(
    val topic: TopicNode,
    val reason: String,
    val priority: Int // Lower = higher priority
) {
    companion object {
        const val PRIORITY_PREREQ_NEED = 1
        const val PRIORITY_READY_TO_LEARN = 2
        const val PRIORITY_NEEDS_REVIEW = 3
        const val PRIORITY_LOW = 100
    }
}
