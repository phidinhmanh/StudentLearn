package com.knowledgemap.app.domain.usecase

import com.knowledgemap.app.data.local.dao.AssessmentHistoryDao
import com.knowledgemap.app.data.local.dao.TopicEdgeDao
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.data.local.entity.AssessmentHistoryEntity
import com.knowledgemap.app.data.remote.GeminiQuizGenerator
import com.knowledgemap.app.domain.model.QuizQuestion
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Assessment UseCase - orchestrates quiz generation + scoring
 * FR-14: Persist to DB BEFORE update UI
 * CON-A05: Validate 4 fields, skip invalid
 */
@Singleton
class AssessmentUseCase @Inject constructor(
    private val quizGenerator: GeminiQuizGenerator,
    private val skillLevelCalculator: SkillLevelCalculator,
    private val topicNodeDao: TopicNodeDao,
    private val topicEdgeDao: TopicEdgeDao,
    private val assessmentHistoryDao: AssessmentHistoryDao
) {
    data class QuizSession(
        val topicId: String,
        val topicName: String,
        val questions: List<QuizQuestion>,
        val currentQuestionIndex: Int = 0,
        val answers: Map<Int, Int> = emptyMap(),
        val timestamp: Long = System.currentTimeMillis()
    ) {
        val isComplete: Boolean get() = answers.size == questions.size
        val correctCount: Int get() = answers.count { (index, answer) ->
            questions.getOrNull(index)?.correctIndex == answer
        }
    }

    data class AssessmentResultDto(
        val success: Boolean,
        val topicId: String,
        val score: Int,
        val totalQuestions: Int,
        val skillBefore: Int,
        val skillAfter: Int,
        val questions: List<QuizQuestion>,
        val answers: Map<Int, Int>,
        val error: String?
    )

    suspend fun generateQuiz(topicId: String): Result<QuizSession> {
        val topic = topicNodeDao.getById(topicId)
            ?: return Result.failure(Exception("Topic not found: $topicId"))

        val prereqIds = topicEdgeDao.getAllPrerequisiteIds(topicId)
        val prereqNames = prereqIds.mapNotNull { topicNodeDao.getById(it)?.name }

        val result = quizGenerator.generateQuiz(
            topicName = topic.name,
            prerequisiteTopics = prereqNames,
            currentSkillLevel = topic.skillLevel,
            difficulty = topic.difficulty
        )

        return if (result.success && result.questions.isNotEmpty()) {
            Result.success(
                QuizSession(
                    topicId = topicId,
                    topicName = topic.name,
                    questions = result.questions
                )
            )
        } else {
            Result.failure(Exception(result.error ?: "Failed to generate quiz"))
        }
    }

    suspend fun submitQuiz(session: QuizSession): AssessmentResultDto {
        val topic = topicNodeDao.getById(session.topicId)
            ?: return AssessmentResultDto(
                success = false,
                topicId = session.topicId,
                score = 0,
                totalQuestions = 0,
                skillBefore = 0,
                skillAfter = 0,
                questions = emptyList(),
                answers = emptyMap(),
                error = "Topic not found"
            )

        val skillBefore = topic.skillLevel
        val correctCount = session.correctCount
        val skillAfter = skillLevelCalculator.calculateAfterAssessment(correctCount, skillBefore)

        // FR-14: Persist to DB FIRST
        val timestamp = System.currentTimeMillis()
        val historyEntity = AssessmentHistoryEntity(
            topicId = session.topicId,
            score = correctCount,
            skillBefore = skillBefore,
            skillAfter = skillAfter,
            timestamp = timestamp,
            source = "gemini"
        )
        assessmentHistoryDao.insert(historyEntity)

        // THEN update topic
        topicNodeDao.updateSkillLevel(session.topicId, skillAfter, timestamp)

        return AssessmentResultDto(
            success = true,
            topicId = session.topicId,
            score = correctCount,
            totalQuestions = session.questions.size,
            skillBefore = skillBefore,
            skillAfter = skillAfter,
            questions = session.questions,
            answers = session.answers,
            error = null
        )
    }
}