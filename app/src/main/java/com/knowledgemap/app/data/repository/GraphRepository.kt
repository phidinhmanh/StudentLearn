package com.knowledgemap.app.data.repository

import com.knowledgemap.app.data.local.dao.TopicEdgeDao
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.data.local.entity.TopicEdgeEntity
import com.knowledgemap.app.data.local.entity.TopicNodeEntity
import com.knowledgemap.app.domain.model.EdgeRelation
import com.knowledgemap.app.domain.model.TopicEdge
import com.knowledgemap.app.domain.model.TopicNode
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Repository for saving/loading knowledge graph
 */
@Singleton
class GraphRepository @Inject constructor(
    private val topicNodeDao: TopicNodeDao,
    private val topicEdgeDao: TopicEdgeDao
) {
    suspend fun saveNodes(nodes: List<TopicNode>) {
        topicNodeDao.insertAll(nodes.map { it.toEntity() })
    }

    suspend fun saveEdges(edges: List<TopicEdge>) {
        topicEdgeDao.insertAll(edges.map { it.toEntity() })
    }

    suspend fun getAllNodes(): List<TopicNode> {
        val entities = mutableListOf<TopicNodeEntity>()
        topicNodeDao.getAllBySubject("toan10").collect { entities.addAll(it) }
        return entities.map { it.toDomain() }
    }

    suspend fun getAllEdges(): List<TopicEdge> {
        val entities = mutableListOf<TopicEdgeEntity>()
        topicEdgeDao.getAll().collect { entities.addAll(it) }
        return entities.map { it.toDomain() }
    }

    suspend fun clearAll() {
        topicEdgeDao.deleteAll()
        topicNodeDao.deleteAllBySubject("toan10")
    }

    private fun TopicNode.toEntity() = TopicNodeEntity(
        id = id,
        name = name,
        desc = desc,
        difficulty = difficulty,
        chapter = chapter,
        subject = subject,
        skillLevel = skillLevel,
        lastAssessed = lastAssessed
    )

    private fun TopicEdge.toEntity() = TopicEdgeEntity(
        fromId = fromId,
        toId = toId,
        relation = relation.toDbString(),
        weight = weight
    )

    private fun TopicNodeEntity.toDomain() = TopicNode(
        id = id,
        name = name,
        desc = desc,
        difficulty = difficulty,
        chapter = chapter,
        subject = subject,
        skillLevel = skillLevel,
        lastAssessed = lastAssessed
    )

    private fun TopicEdgeEntity.toDomain() = TopicEdge(
        fromId = fromId,
        toId = toId,
        relation = EdgeRelation.fromString(relation),
        weight = weight
    )
}