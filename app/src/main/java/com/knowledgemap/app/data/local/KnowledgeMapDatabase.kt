package com.knowledgemap.app.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.knowledgemap.app.data.local.dao.AssessmentHistoryDao
import com.knowledgemap.app.data.local.dao.SessionLogDao
import com.knowledgemap.app.data.local.dao.TopicEdgeDao
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.data.local.entity.AssessmentHistoryEntity
import com.knowledgemap.app.data.local.entity.SessionLogEntity
import com.knowledgemap.app.data.local.entity.TopicEdgeEntity
import com.knowledgemap.app.data.local.entity.TopicNodeEntity

/**
 * KnowledgeMap Database - Room Database
 *
 * Schema: 4 tables (topic_node, topic_edge, assessment_history, session_log)
 * CON-P04: Database migration path
 */
@Database(
    entities = [
        TopicNodeEntity::class,
        TopicEdgeEntity::class,
        AssessmentHistoryEntity::class,
        SessionLogEntity::class
    ],
    version = 1,
    exportSchema = true
)
abstract class KnowledgeMapDatabase : RoomDatabase() {

    abstract fun topicNodeDao(): TopicNodeDao

    abstract fun topicEdgeDao(): TopicEdgeDao

    abstract fun assessmentHistoryDao(): AssessmentHistoryDao

    abstract fun sessionLogDao(): SessionLogDao

    companion object {
        const val DATABASE_NAME = "knowledgemap.db"

        // Migration strategy: fallbackToDestructiveMigration for MVP
        // CON-P04: Will implement proper migrations in future versions
    }
}