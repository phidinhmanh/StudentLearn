package com.knowledgemap.app.data.local.dao

import androidx.room.Dao
import androidx.room.Delete
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import com.knowledgemap.app.data.local.entity.TopicEdgeEntity
import kotlinx.coroutines.flow.Flow

/**
 * Data Access Object for TopicEdge
 *
 * CON-D01: Directed graph với labels (prerequisite | sequenceOf | relatedTo)
 * CON-G03: Transitive prerequisite (A→B→C = A prerequisite of C)
 */
@Dao
interface TopicEdgeDao {

    @Query("SELECT * FROM topic_edge")
    fun getAll(): Flow<List<TopicEdgeEntity>>

    @Query("SELECT * FROM topic_edge WHERE from_id = :fromId")
    fun getOutgoingEdges(fromId: String): Flow<List<TopicEdgeEntity>>

    @Query("SELECT * FROM topic_edge WHERE to_id = :toId")
    fun getIncomingEdges(toId: String): Flow<List<TopicEdgeEntity>>

    @Query("SELECT * FROM topic_edge WHERE relation = :relation")
    fun getByRelation(relation: String): Flow<List<TopicEdgeEntity>>

    @Query("SELECT * FROM topic_edge WHERE from_id = :fromId AND relation = 'prerequisite'")
    fun getPrerequisites(fromId: String): Flow<List<TopicEdgeEntity>>

    @Query("SELECT * FROM topic_edge WHERE to_id = :toId AND relation = 'prerequisite'")
    fun getPrerequisiteEdges(toId: String): Flow<List<TopicEdgeEntity>>

    /** Lấy tất cả prerequisite IDs của một topic (CON-G03: transitive) */
    @Query("""
        WITH RECURSIVE prereqs AS (
            SELECT from_id, to_id, 1 as depth
            FROM topic_edge
            WHERE to_id = :topicId AND relation = 'prerequisite'

            UNION ALL

            SELECT e.from_id, e.to_id, p.depth + 1
            FROM topic_edge e
            INNER JOIN prereqs p ON e.to_id = p.from_id
            WHERE e.relation = 'prerequisite' AND p.depth < 10
        )
        SELECT DISTINCT from_id FROM prereqs
    """)
    suspend fun getAllPrerequisiteIds(topicId: String): List<String>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(edge: TopicEdgeEntity)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(edges: List<TopicEdgeEntity>)

    @Delete
    suspend fun delete(edge: TopicEdgeEntity)

    @Query("DELETE FROM topic_edge")
    suspend fun deleteAll()
}