package com.knowledgemap.app.data.remote

import com.knowledgemap.app.data.remote.dto.*
import retrofit2.Response
import retrofit2.http.*

interface StudentLearnApi {

    // ── Auth ────────────────────────────────────────────────────────────────

    @POST("api/v1/auth/register")
    suspend fun register(@Body body: UserRegisterRequest): Response<TokenResponse>

    @POST("api/v1/auth/login")
    suspend fun login(@Body body: UserLoginRequest): Response<TokenResponse>

    // ── Documents ────────────────────────────────────────────────────────────

    @GET("api/v1/documents/")
    suspend fun getDocuments(): Response<List<DocumentResponse>>

    @Multipart
    @POST("api/v1/documents/ingest")
    suspend fun ingestDocument(
        @Part file: okhttp3.MultipartBody.Part,
        @Part("subject") subject: okhttp3.RequestBody
    ): Response<DocumentIngestResponse>

    @GET("api/v1/documents/status/{taskId}")
    suspend fun getIngestStatus(@Path("taskId") taskId: String): Response<TaskStatusResponse>

    @GET("api/v1/documents/{docId}/topics")
    suspend fun getDocumentTopics(@Path("docId") docId: String): Response<List<TopicResponse>>

    // ── Quiz ─────────────────────────────────────────────────────────────────

    @GET("api/v1/quiz/{topicId}")
    suspend fun getQuiz(@Path("topicId") topicId: String): Response<QuizResponse>

    @POST("api/v1/quiz/submit")
    suspend fun submitQuiz(@Body body: QuizSubmitRequest): Response<QuizSubmitResponse>

    // ── Learning Path ────────────────────────────────────────────────────────

    @GET("api/v1/learning-path/{userId}")
    suspend fun getLearningPath(
        @Path("userId") userId: String,
        @Query("goal") goal: String = "master_all"
    ): Response<LearningPathResponse>

    // ── Progress ─────────────────────────────────────────────────────────────

    @GET("api/v1/progress/{userId}")
    suspend fun getProgress(@Path("userId") userId: String): Response<List<ProgressResponse>>

    @PUT("api/v1/progress/{userId}/{topicId}")
    suspend fun updateProgress(
        @Path("userId") userId: String,
        @Path("topicId") topicId: String,
        @Body body: ProgressUpdateRequest
    ): Response<Map<String, String>>

    // ── Graph RAG ────────────────────────────────────────────────────────────

    @POST("api/v1/graph-rag/query")
    suspend fun queryGraphRag(@Body body: GraphRagQueryRequest): Response<GraphRagQueryResponse>

    @GET("api/v1/graph-rag/visualize/{documentId}")
    suspend fun visualizeGraph(@Path("documentId") documentId: String): Response<GraphVisualizationResponse>

    // ── Health ────────────────────────────────────────────────────────────────

    @GET("api/v1/health")
    suspend fun healthCheck(): Response<HealthResponse>
}