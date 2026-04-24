package com.knowledgemap.app.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.ForeignKey
import androidx.room.Index

/**
 * TopicEdge Entity - Represents a directed edge in the Knowledge Graph
 *
 * CON-D01: Graph phải là directed graph có nhãn
 * Labels: prerequisite | sequenceOf | relatedTo
 */
@Entity(
    tableName = "topic_edge",
    primaryKeys = ["from_id", "to_id", "relation"],
    foreignKeys = [
        ForeignKey(
            entity = TopicNodeEntity::class,
            parentColumns = ["id"],
            childColumns = ["from_id"],
            onDelete = ForeignKey.CASCADE
        ),
        ForeignKey(
            entity = TopicNodeEntity::class,
            parentColumns = ["id"],
            childColumns = ["to_id"],
            onDelete = ForeignKey.CASCADE
        )
    ],
    indices = [
        Index("from_id"),
        Index("to_id")
    ]
)
data class TopicEdgeEntity(
    /** Node nguồn (topic phải học trước) */
    @ColumnInfo(name = "from_id")
    val fromId: String,

    /** Node đích */
    @ColumnInfo(name = "to_id")
    val toId: String,

    /**
     * Loại quan hệ:
     * - prerequisite: Phải học A trước B (A → B)
     * - sequenceOf: Cùng chương, thứ tự học
     * - relatedTo: Liên quan nhưng không bắt buộc
     */
    @ColumnInfo(name = "relation")
    val relation: String,

    /** Trọng số cạnh - dùng khi có nhiều prerequisite */
    @ColumnInfo(name = "weight")
    val weight: Float = 1.0f
)

/** Edge relation types (CON-D01) */
object EdgeRelation {
    const val PREREQUISITE = "prerequisite"
    const val SEQUENCE_OF = "sequenceOf"
    const val RELATED_TO = "relatedTo"

    val VALID_TYPES = listOf(PREREQUISITE, SEQUENCE_OF, RELATED_TO)
}