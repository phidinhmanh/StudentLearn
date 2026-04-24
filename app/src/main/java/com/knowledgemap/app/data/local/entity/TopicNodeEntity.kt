package com.knowledgemap.app.data.local.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * TopicNode Entity - Represents a topic/node in the Knowledge Graph
 *
 * CON-D02: skill_level chỉ nhận giá trị {0, 1, 2, 3}
 * CON-G02: Node phải có đủ: id, name, desc, difficulty, prereq
 */
@Entity(tableName = "topic_node")
data class TopicNodeEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,

    @ColumnInfo(name = "name")
    val name: String,

    @ColumnInfo(name = "desc")
    val desc: String,

    /** Difficulty: 1=Dễ, 2=TB, 3=Khó (CON-G02) */
    @ColumnInfo(name = "difficulty")
    val difficulty: Int,

    @ColumnInfo(name = "chapter")
    val chapter: String,

    @ColumnInfo(name = "subject")
    val subject: String = "toan10",

    /** Skill Level: 0=Chưa học, 1=Cần ôn, 2=Đang học, 3=Đã vững (CON-D02) */
    @ColumnInfo(name = "skill_level")
    val skillLevel: Int = 0,

    /** Unix timestamp của lần assessment gần nhất */
    @ColumnInfo(name = "last_assessed")
    val lastAssessed: Long? = null
)