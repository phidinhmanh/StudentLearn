package com.knowledgemap.app.data.remote.dto

// Auth
data class UserRegisterRequest(
    val email: String,
    val password: String,
    val name: String
)

data class UserLoginRequest(
    val email: String,
    val password: String
)

data class TokenResponse(
    val access_token: String,
    val token_type: String = "bearer"
)

// Health
data class HealthResponse(
    val status: String,
    val service: String? = null,
    val version: String? = null,
    val graph_provider: String? = null,
    val connection: Map<String, Any>? = null
)

// Document
data class DocumentIngestResponse(
    val doc_id: String,
    val filename: String,
    val task_id: String,
    val status: String
)

data class TaskStatusResponse(
    val task_id: String,
    val status: String,
    val progress: Int,
    val message: String,
    val created_at: String,
    val completed_at: String? = null,
    val error: Map<String, Any>? = null
)

data class DocumentResponse(
    val id: String,
    val filename: String,
    val uploaded_at: String
)

data class TopicResponse(
    val id: String,
    val name: String,
    val description: String? = null,
    val type: String? = null,
    val difficulty: String? = null,
    val subject: String? = null
)

// Quiz
data class QuizResponse(
    val quiz_id: String,
    val topic_id: String,
    val questions: List<QuizQuestionDto>
)

data class QuizQuestionDto(
    val id: String,
    val text: String,
    val type: String = "multiple_choice",
    val options: List<String> = emptyList(),
    val explanation: String? = null,
    val cognitive_level: String = "application"
)

data class QuizSubmitRequest(
    val quiz_id: String,
    val answers: List<QuizAnswerDto>
)

data class QuizAnswerDto(
    val question_id: String,
    val answer: String
)

data class QuizSubmitResponse(
    val quiz_id: String,
    val topic_id: String,
    val correct_count: Int,
    val total: Int,
    val score: String,
    val skill_level: Int,
    val feedback: String,
    val results: List<QuizResultDetail> = emptyList()
)

data class QuizResultDetail(
    val question_id: String,
    val question_text: String,
    val user_answer: String,
    val correct_answer: String,
    val is_correct: Boolean,
    val explanation: String? = null
)

// Learning Path
data class LearningPathResponse(
    val path: List<LearningPathItem> = emptyList(),
    val summary: String? = null
)

data class LearningPathItem(
    val topic_id: String,
    val name: String,
    val priority: Int,
    val reason: String,
    val estimated_time: String,
    val status: String
)

// Progress
data class ProgressResponse(
    val topic_id: String,
    val topic_name: String,
    val skill_level: Int,
    val last_attempt: String? = null
)

data class ProgressUpdateRequest(
    val skill_level: Int
)

// Graph RAG
data class GraphRagQueryRequest(
    val query: String,
    val session_id: String = "default-session"
)

data class GraphRagQueryResponse(
    val answer: String
)

data class GraphVisualizationResponse(
    val nodes: List<GraphNode> = emptyList(),
    val links: List<GraphLink> = emptyList()
)

data class GraphNode(
    val id: String,
    val label: String,
    val skill_level: Int = 1,
    val type: String = "concept"
)

data class GraphLink(
    val source: String,
    val target: String,
    val type: String = "relatedTo"
)