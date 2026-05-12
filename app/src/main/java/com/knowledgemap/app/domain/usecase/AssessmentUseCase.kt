package com.knowledgemap.app.domain.usecase

import com.knowledgemap.app.data.local.dao.AssessmentHistoryDao
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.data.local.entity.AssessmentHistoryEntity
import com.knowledgemap.app.data.remote.StudentLearnApi
import com.knowledgemap.app.domain.model.QuizQuestion
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AssessmentUseCase @Inject constructor(
    private val api: StudentLearnApi,
    private val skillLevelCalculator: SkillLevelCalculator,
    private val topicNodeDao: TopicNodeDao,
    private val assessmentHistoryDao: AssessmentHistoryDao
) {
    data class QuizSession(
        val quizId: String,
        val topicId: String,
        val topicName: String,
        val questions: List<QuizQuestion>,
        val answers: Map<Int, Int> = emptyMap(),
        val timestamp: Long = System.currentTimeMillis()
    )

    data class AssessmentResultDto(
        val success: Boolean,
        val topicId: String,
        val score: Int,
        val totalQuestions: Int,
        val skillBefore: Int,
        val skillAfter: Int,
        val error: String?
    )

    suspend fun generateQuiz(topicId: String): Result<QuizSession> {
        val topic = topicNodeDao.getById(topicId)
            ?: return Result.failure(Exception("Topic not found"))

        return try {
            val response = api.getQuiz(topicId)
            if (response.isSuccessful && response.body() != null) {
                val quizDto = response.body()!!
                Result.success(
                    QuizSession(
                        quizId = quizDto.quiz_id,
                        topicId = topicId,
                        topicName = topic.name,
                        questions = quizDto.questions.mapIndexed { index, q ->
                            QuizQuestion(
                                question = q.text,
                                options = q.options,
                                correctIndex = -1, // Backend hides this
                                explanation = q.explanation ?: ""
                            )
                        }
                    )
                )
            } else {
                Result.failure(Exception("Failed to load quiz from server"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun submitQuiz(session: QuizSession, selectedAnswers: Map<Int, Int>): Result<AssessmentResultDto> {
        val topic = topicNodeDao.getById(session.topicId)
            ?: return Result.failure(Exception("Topic not found"))

        val answersDto = selectedAnswers.map { (index, answer) ->
            com.knowledgemap.app.data.remote.dto.QuizAnswerDto(
                question_id = index.toString(), // or real ID if DTO has it
                answer = answer.toString()
            )
        }

        return try {
            val response = api.submitQuiz(
                com.knowledgemap.app.data.remote.dto.QuizSubmitRequest(
                    quiz_id = session.quizId,
                    answers = answersDto
                )
            )

            if (response.isSuccessful && response.body() != null) {
                val result = response.body()!!
                val skillBefore = topic.skillLevel
                val skillAfter = result.skill_level

                // Persist
                val timestamp = System.currentTimeMillis()
                assessmentHistoryDao.insert(
                    AssessmentHistoryEntity(
                        topicId = session.topicId,
                        score = result.correct_count,
                        skillBefore = skillBefore,
                        skillAfter = skillAfter,
                        timestamp = timestamp,
                        source = "backend"
                    )
                )
                topicNodeDao.updateSkillLevel(session.topicId, skillAfter, timestamp)

                Result.success(
                    AssessmentResultDto(
                        success = true,
                        topicId = session.topicId,
                        score = result.correct_count,
                        totalQuestions = result.total,
                        skillBefore = skillBefore,
                        skillAfter = skillAfter,
                        error = null
                    )
                )
            } else {
                Result.failure(Exception("Submission failed"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}