package com.knowledgemap.app.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.knowledgemap.app.data.local.entity.AssessmentHistoryEntity
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for AssessmentHistory
 *
 * FR-14: Kết quả phải persist vào DB TRƯỚC KHI update UI
 */
@Dao
interface AssessmentHistoryDao {

    @Query("SELECT * FROM assessment_history WHERE topic_id = :topicId ORDER BY timestamp DESC")
    fun getByTopicId(topicId: String): Flow<List<AssessmentHistoryEntity>>

    @Query("SELECT * FROM assessment_history ORDER BY timestamp DESC")
    fun getAll(): Flow<List<AssessmentHistoryEntity>>

    @Query("SELECT * FROM assessment_history ORDER BY timestamp DESC LIMIT :limit")
    fun getRecent(limit: Int): Flow<List<AssessmentHistoryEntity>>

    @Query("SELECT * FROM assessment_history WHERE topic_id = :topicId ORDER BY timestamp DESC LIMIT 1")
    suspend fun getLatestByTopicId(topicId: String): AssessmentHistoryEntity?

    @Query("SELECT AVG(score) FROM assessment_history WHERE topic_id = :topicId")
    suspend fun getAverageScore(topicId: String): Float?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(history: AssessmentHistoryEntity): Long

    @Query("DELETE FROM assessment_history WHERE topic_id = :topicId")
    suspend fun deleteByTopicId(topicId: String)

    @Query("SELECT COUNT(*) FROM assessment_history WHERE topic_id = :topicId")
    suspend fun getCountByTopicId(topicId: String): Int
}