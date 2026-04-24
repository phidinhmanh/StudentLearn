package com.knowledgemap.app.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index
import androidx.room.PrimaryKey

/**
 * SessionLog Entity - Lưu lịch sử buổi học tự ghi
 *
 * FR-24: Không xóa history tự động
 */
@Entity(
    tableName = "session_log",
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
data class SessionLogEntity(
    @PrimaryKey(autoGenerate = true)
    @ColumnInfo(name = "id")
    val id: Long = 0,

    @ColumnInfo(name = "topic_id")
    val topicId: String,

    @ColumnInfo(name = "started_at")
    val startedAt: Long,

    @ColumnInfo(name = "ended_at")
    val endedAt: Long? = null,

    /**
     * Self-rating từ user:
     * - 0: Chưa hiểu → skill level -1
     * - 1: Cần ôn lại → skill level giữ nguyên
     * - 2: Hiểu rõ → skill level +1
     */
    @ColumnInfo(name = "self_rating")
    val selfRating: Int? = null
)

/** Self rating values (FR-22) */
object SelfRating {
    const val CHUA_HIEU = 0
    const val CAN_ON = 1
    const val HIEU_RO = 2
}