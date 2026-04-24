package com.knowledgemap.app.data.local.dao

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.knowledgemap.app.data.local.entity.SessionLogEntity
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for SessionLog
 *
 * FR-24: Không xóa history tự động
 */
@Dao
interface SessionLogDao {

    @Query("SELECT * FROM session_log WHERE topic_id = :topicId ORDER BY started_at DESC")
    fun getByTopicId(topicId: String): Flow<List<SessionLogEntity>>

    @Query("SELECT * FROM session_log ORDER BY started_at DESC")
    fun getAll(): Flow<List<SessionLogEntity>>

    @Query("SELECT * FROM session_log ORDER BY started_at DESC LIMIT :limit")
    fun getRecent(limit: Int): Flow<List<SessionLogEntity>>

    @Query("SELECT * FROM session_log WHERE ended_at IS NULL ORDER BY started_at DESC LIMIT 1")
    suspend fun getActiveSession(): SessionLogEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(session: SessionLogEntity): Long

    @Query("UPDATE session_log SET ended_at = :endedAt, self_rating = :selfRating WHERE id = :id")
    suspend fun endSession(id: Long, endedAt: Long, selfRating: Int?)

    @Query("SELECT SUM(ended_at - started_at) FROM session_log WHERE topic_id = :topicId AND ended_at IS NOT NULL")
    suspend fun getTotalStudyTime(topicId: String): Long?

    @Query("SELECT COUNT(*) FROM session_log WHERE topic_id = :topicId")
    suspend fun getSessionCount(topicId: String): Int
}