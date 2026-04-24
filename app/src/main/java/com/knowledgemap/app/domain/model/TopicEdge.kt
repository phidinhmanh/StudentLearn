package com.knowledgemap.app.domain.model

/**
 * Domain model cho TopicEdge
 * Mapping từ TopicEdgeEntity
 */
data class TopicEdge(
    val fromId: String,
    val toId: String,
    val relation: EdgeRelation,
    val weight: Float = 1.0f
)

/** Edge relation types (CON-D01) */
enum class EdgeRelation {
    PREREQUISITE,
    SEQUENCE_OF,
    RELATED_TO;

    companion object {
        fun fromString(value: String): EdgeRelation = when (value.lowercase()) {
            "prerequisite" -> PREREQUISITE
            "sequenceof" -> SEQUENCE_OF
            "relatedto" -> RELATED_TO
            else -> PREREQUISITE
        }
    }

    fun toDbString(): String = when (this) {
        PREREQUISITE -> "prerequisite"
        SEQUENCE_OF -> "sequenceOf"
        RELATED_TO -> "relatedTo"
    }
}