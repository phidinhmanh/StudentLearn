package com.knowledgemap.app.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * AssessmentHistory Entity - Lưu lịch sử đánh giá skill level
 *
 * FR-14: Kết quả phải persist vào DB TRƯỚC KHI update UI
 * FR-23: Ưu tiên Skill Level THẤP HƠN khi mâu thuẫn
 */
@Entity(
    tableName = "assessment_history",
    foreignKeys = [
        ForeignKey(
            entity = TopicNodeEntity::class,
            parentColumns = ["id"],
            childColumns = ["topic_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [Index("topic_id")]
)
data class AssessmentHistoryEntity(
    @PrimaryKey(autoGenerate = true)
    @ColumnInfo(name = "id")
    val id: Long = 0,

    @ColumnInfo(name = "topic_id")
    val topicId: String,

    /** Số câu đúng (0-5) */
    @ColumnInfo(name = "score")
    val score: Int,

    @ColumnInfo(name = "skill_before")
    val skillBefore: Int,

    @ColumnInfo(name = "skill_after")
    val skillAfter: Int,

    @ColumnInfo(name = "timestamp")
    val timestamp: Long,

    /**
     * Nguồn đánh giá:
     * - gemini: Do AI (Gemini API) generate quiz
     * - self_report: Do user tự đánh giá
     */
    @ColumnInfo(name = "source")
    val source: String
)

/** Assessment source types */
object AssessmentSource {
    const val GEMINI = "gemini"
    const val SELF_REPORT = "self_report"
}