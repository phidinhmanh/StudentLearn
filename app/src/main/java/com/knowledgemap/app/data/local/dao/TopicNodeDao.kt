package com.knowledgemap.app.data.local.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import com.knowledgemap.app.data.local.entity.TopicNodeEntity
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for TopicNode
 *
 * CON-D02: skill_level ∈ {0, 1, 2, 3}
 * CON-D03: Prerequisite check trước recommend
 */
@Dao
interface TopicNodeDao {

    @Query("SELECT * FROM topic_node WHERE subject = :subject ORDER BY chapter")
    fun getAllBySubject(subject: String = "toan10"): Flow<List<TopicNodeEntity>>

    @Query("SELECT * FROM topic_node WHERE id = :id")
    suspend fun getById(id: String): TopicNodeEntity?

    @Query("SELECT * FROM topic_node WHERE id = :id")
    fun getByIdFlow(id: String): Flow<TopicNodeEntity?>

    @Query("SELECT * FROM topic_node WHERE chapter = :chapter ORDER BY name")
    fun getByChapter(chapter: String): Flow<List<TopicNodeEntity>>

    @Query("SELECT * FROM topic_node WHERE skill_level = :skillLevel")
    fun getBySkillLevel(skillLevel: Int): Flow<List<TopicNodeEntity>>

    @Query("SELECT * FROM topic_node WHERE skill_level IN (:skillLevels)")
    fun getBySkillLevels(skillLevels: List<Int>): Flow<List<TopicNodeEntity>>

    @Query("SELECT * FROM topic_node WHERE skill_level >= 2")
    fun getLearnedTopics(): Flow<List<TopicNodeEntity>>

    @Query("SELECT DISTINCT chapter FROM topic_node WHERE subject = :subject ORDER BY chapter")
    fun getChapters(subject: String = "toan10"): Flow<List<String>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(topic: TopicNodeEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(topics: List<TopicNodeEntity>)

    @Update
    suspend fun update(topic: TopicNodeEntity)

    @Query("UPDATE topic_node SET skill_level = :skillLevel, last_assessed = :timestamp WHERE id = :id")
    suspend fun updateSkillLevel(id: String, skillLevel: Int, timestamp: Long)

    @Delete
    suspend fun delete(topic: TopicNodeEntity)

    @Query("DELETE FROM topic_node WHERE subject = :subject")
    suspend fun deleteAllBySubject(subject: String)

    @Query("SELECT COUNT(*) FROM topic_node WHERE subject = :subject")
    suspend fun getCount(subject: String = "toan10"): Int

    @Query("SELECT COUNT(*) FROM topic_node WHERE subject = :subject AND skill_level >= 2")
    suspend fun getLearnedCount(subject: String = "toan10"): Int
}