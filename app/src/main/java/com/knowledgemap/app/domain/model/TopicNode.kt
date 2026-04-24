package com.knowledgemap.app.domain.model

/**
 * Domain model cho TopicNode
 * Mapping từ TopicNodeEntity
 */
data class TopicNode(
    val id: String,
    val name: String,
    val desc: String,
    val difficulty: Int, // 1=Dễ, 2=TB, 3=Khó
    val chapter: String,
    val subject: String = "toan10",
    val skillLevel: Int, // 0=Chưa học, 1=Cần ôn, 2=Đang học, 3=Đã vững
    val lastAssessed: Long? = null
) {
    /** Kiểm tra topic có đang ở trạng thái "mới" không */
    val isNew: Boolean get() = skillLevel == 0 && lastAssessed == null

    /** Kiểm tra topic đã được học chưa */
    val isLearned: Boolean get() = skillLevel >= 2

    /** Lấy trạng thái skill level (matching với Cyber-Academic design) */
    val status: TopicStatus get() = TopicStatus.fromLevel(skillLevel)
}

/** Trạng thái Topic - matching với DESIGN.md */
enum class TopicStatus(val level: Int, val label: String) {
    LOCKED(0, "Chưa mở"),      // Locked
    GAP(1, "Lỗ hổng"),         // Gap
    LEARNING(2, "Đang học"),   // Learning
    MASTERED(3, "Đã vững");    // Mastered

    companion object {
        fun fromLevel(level: Int): TopicStatus = when (level) {
            0 -> LOCKED
            1 -> GAP
            2 -> LEARNING
            3 -> MASTERED
            else -> LOCKED
        }
    }
}