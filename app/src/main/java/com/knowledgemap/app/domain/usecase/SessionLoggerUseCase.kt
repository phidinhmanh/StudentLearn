package com.knowledgemap.app.domain.usecase

import com.knowledgemap.app.data.local.dao.SessionLogDao
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.data.local.entity.SessionLogEntity
import kotlinx.coroutines.flow.first
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Session Logger UseCase
 * FR-22: Apply self-rating to update skill level
 * FR-24: Never delete history automatically
 */
@Singleton
class SessionLoggerUseCase @Inject constructor(
    private val sessionLogDao: SessionLogDao,
    private val topicNodeDao: TopicNodeDao,
    private val selfRatingMapper: SelfRatingMapper
) {
    suspend fun startSession(topicId: String): Long {
        val session = SessionLogEntity(
            topicId = topicId,
            startedAt = System.currentTimeMillis(),
            endedAt = null,
            selfRating = null
        )
        sessionLogDao.insert(session)
        return session.id
    }

    suspend fun endSession(sessionId: Long, selfRating: Int): Boolean {
        val session = sessionLogDao.getActiveSession() ?: return false

        sessionLogDao.endSession(
            id = sessionId,
            endedAt = System.currentTimeMillis(),
            selfRating = selfRating
        )

        val topic = topicNodeDao.getById(session.topicId) ?: return true
        val newSkillLevel = selfRatingMapper.applyRating(topic.skillLevel, selfRating)
        topicNodeDao.updateSkillLevel(
            topic.id,
            newSkillLevel,
            System.currentTimeMillis()
        )

        return true
    }

    suspend fun getSessionsForTopic(topicId: String): List<SessionLogEntity> {
        return sessionLogDao.getByTopicId(topicId).first()
    }

    suspend fun getAllSessions(): List<SessionLogEntity> {
        return sessionLogDao.getAll().first()
    }
}
