package com.knowledgemap.app.data.remote

import com.knowledgemap.app.domain.model.QuizQuestion
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Query

/**
 * Retrofit service interface for Cognee backend API.
 * Allows Android app to call Python backend for knowledge graph extraction.
 */
interface CogneeApiService {

    @GET("api/v1/health")
    suspend fun healthCheck(): Response<HealthResponse>

    @POST("api/v1/ingest")
    suspend fun ingestDocument(@Body request: IngestRequest): Response<IngestResponse>

    @POST("api/v1/query")
    suspend fun queryContext(@Body request: QueryRequest): Response<QueryResponse>
}

// Request/Response DTOs
data class HealthResponse(
    val status: String,
    val version: String,
    val gemini_configured: Boolean
)

data class IngestRequest(
    val document_text: String,
    val chapter: String,
    val subject: String = "toan10"
)

data class IngestResponse(
    val success: Boolean,
    val nodes: List<TopicNodeDto>,
    val edges: List<TopicEdgeDto>,
    val chunks_processed: Int,
    val message: String?
)

data class TopicNodeDto(
    val id: String,
    val name: String,
    val desc: String = "",
    val difficulty: Int = 1,
    val chapter: Int = 1,
    val subject: String = "toan10",
    val skill_level: Int = 0,
    val last_assessed: String? = null
)

data class TopicEdgeDto(
    val from_id: String,
    val to_id: String,
    val relation: String = "relatedTo",
    val weight: Double = 1.0
)

data class QueryRequest(
    val query: String,
    val top_k: Int = 5
)

data class QueryResponse(
    val success: Boolean,
    val context: String = "",
    val related_topics: List<String> = emptyList(),
    val message: String?
)