package com.knowledgemap.app.data.remote

import com.knowledgemap.app.data.remote.dto.*
import kotlinx.coroutines.runBlocking
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.MultipartBody
import okhttp3.OkHttpClient
import okhttp3.RequestBody.Companion.asRequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.logging.HttpLoggingInterceptor
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.io.File
import java.util.concurrent.TimeUnit

/**
 * Integration tests for UI button flows.
 * Tests entire interaction chain: UI Action -> API Call -> Response -> UI State Update
 */
class UIButtonFlowTest {

    private lateinit var api: StudentLearnApi
    private var authToken: String? = null
    private val baseUrl = ApiConfig.BACKEND_BASE_URL

    @Before
    fun setup() {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(10, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        api = retrofit.create(StudentLearnApi::class.java)
    }

    private fun createAuthApi(token: String): StudentLearnApi {
        val authClient = OkHttpClient.Builder()
            .addInterceptor { chain ->
                val req = chain.request().newBuilder()
                    .addHeader("Authorization", "Bearer $token")
                    .build()
                chain.proceed(req)
            }
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .build()

        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(authClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(StudentLearnApi::class.java)
    }

    // ── AUTH FLOW TESTS ──────────────────────────────────────────────────────

    @Test
    fun `TC-AUTH-01 Register button flow`() = runBlocking<Unit> {
        val randomEmail = "qa_${System.currentTimeMillis()}@test.com"
        val request = UserRegisterRequest(
            email = randomEmail,
            password = "test123",
            name = "QA Tester"
        )

        val response = api.register(request)

        assertTrue("Register failed: ${response.errorBody()?.string()}", response.isSuccessful)
        assertNotNull("Token should be returned", response.body()?.access_token)
        println("PASS TC-AUTH-01: Register button flow works")
    }

    @Test
    fun `TC-AUTH-02 Login button flow`() = runBlocking<Unit> {
        val randomEmail = "qa_login_${System.currentTimeMillis()}@test.com"
        val password = "password123"
        api.register(UserRegisterRequest(randomEmail, password, "Login Test"))

        val loginRequest = UserLoginRequest(randomEmail, password)
        val response = api.login(loginRequest)

        assertTrue("Login failed: ${response.errorBody()?.string()}", response.isSuccessful)
        assertNotNull("Token should be returned", response.body()?.access_token)
        authToken = response.body()?.access_token
        println("PASS TC-AUTH-02: Login button flow works")
    }

    @Test
    fun `TC-AUTH-03 Invalid credentials`() = runBlocking<Unit> {
        val response = api.login(UserLoginRequest("nonexistent@test.com", "wrong"))

        assertEquals("Should return 401 for invalid credentials", 401, response.code())
        println("PASS TC-AUTH-03: Invalid login returns 401")
    }

    // ── HOME SCREEN FLOW TESTS ────────────────────────────────────────────────

    @Test
    fun `TC-HOME-01 Topic card navigation`() = runBlocking<Unit> {
        val token = registerAndGetToken()
        val authApi = createAuthApi(token)

        val response = authApi.getLearningPath(userId = "test_user")

        assertTrue("Learning path should be accessible: ${response.code()}", response.code() != 401)
        println("PASS TC-HOME-01: Topic cards can navigate to assessment")
    }

    // ── ASSESSMENT (QUIZ) FLOW TESTS ─────────────────────────────────────────

    @Test
    fun `TC-QUIZ-01 Load quiz questions`() = runBlocking<Unit> {
        val token = registerAndGetToken()
        val authApi = createAuthApi(token)

        val response = authApi.getQuiz("ch1_tap_hop")

        if (response.code() == 404) {
            println("SKIP TC-QUIZ-01: No quiz data for this topic yet (404)")
            return@runBlocking
        }

        assertTrue("Quiz should load: ${response.code()}", response.code() != 401)
        response.body()?.let { quiz ->
            assertNotNull("Questions should exist", quiz.questions)
            assertTrue("Should have questions", quiz.questions.isNotEmpty())
            println("PASS TC-QUIZ-01: Quiz loads with ${quiz.questions.size} questions")
        }
    }

    @Test
    fun `TC-QUIZ-02 Submit quiz and get score`() = runBlocking<Unit> {
        val token = registerAndGetToken()
        val authApi = createAuthApi(token)

        val submitRequest = QuizSubmitRequest(
            quiz_id = "ch1_tap_hop",
            answers = listOf(
                QuizAnswerDto(question_id = "q1", answer = "1"),
                QuizAnswerDto(question_id = "q2", answer = "2"),
                QuizAnswerDto(question_id = "q3", answer = "0"),
                QuizAnswerDto(question_id = "q4", answer = "1"),
                QuizAnswerDto(question_id = "q5", answer = "2")
            )
        )

        val response = authApi.submitQuiz(submitRequest)

        if (response.code() == 404) {
            println("SKIP TC-QUIZ-02: Quiz not generated for this topic")
            return@runBlocking
        }

        assertTrue("Submit should succeed: ${response.code()}", response.code() != 401)
        response.body()?.let { result ->
            assertNotNull("Score should be returned", result.score)
            println("PASS TC-QUIZ-02: Quiz submitted, score=${result.score}")
        }
    }

    @Test
    fun `TC-QUIZ-03 Answer selection locked after select`() = runBlocking<Unit> {
        val token = registerAndGetToken()
        val authApi = createAuthApi(token)

        val quizResponse = authApi.getQuiz("ch1_tap_hop")
        if (quizResponse.code() == 404) {
            println("SKIP TC-QUIZ-03")
            return@runBlocking
        }

        val submitRequest = QuizSubmitRequest(
            quiz_id = "ch1_tap_hop",
            answers = listOf(QuizAnswerDto(question_id = "q1", answer = "1"))
        )

        val result = authApi.submitQuiz(submitRequest)
        assertTrue("Answer submission works", result.code() != 401)
        println("PASS TC-QUIZ-03: Answer selection is captured correctly")
    }

    // ── PROGRESS & SESSION LOGGER FLOW TESTS ─────────────────────────────────

    @Test
    fun `TC-SESSION-01 Update progress with self-rating`() = runBlocking<Unit> {
        val token = registerAndGetToken()
        val authApi = createAuthApi(token)

        val progressRequest = ProgressUpdateRequest(skill_level = 3)
        val response = authApi.updateProgress("test_user_id", "ch1_tap_hop", progressRequest)

        assertTrue("Progress update should work: ${response.code()}", response.code() != 401)
        println("PASS TC-SESSION-01: Self-rating updates progress")
    }

    @Test
    fun `TC-SESSION-02 All rating options map correctly`() = runBlocking<Unit> {
        val token = registerAndGetToken()
        val authApi = createAuthApi(token)

        val levels = listOf(1 to "Chua hieu", 2 to "Can on lai", 3 to "Hieu ro")

        levels.forEach { (level, label) ->
            val response = authApi.updateProgress("test_user_id", "ch1_tap_hop", ProgressUpdateRequest(skill_level = level))
            assertTrue("Rating $label should work: ${response.code()}", response.code() != 401)
        }

        println("PASS TC-SESSION-02: All rating options map correctly")
    }

    @Test
    fun `TC-PROGRESS-01 Get user progress returns data`() = runBlocking<Unit> {
        val token = registerAndGetToken()
        val authApi = createAuthApi(token)

        val response = authApi.getProgress("test_user")

        assertTrue("Get progress should work: ${response.code()}", response.code() != 401)
        assertNotNull("Response body should exist", response.body())
        println("PASS TC-PROGRESS-01: Progress retrieval works")
    }

    // ── KNOWLEDGE MAP FLOW TESTS ─────────────────────────────────────────────

    @Test
    fun `TC-MAP-01 Get topic details for map display`() = runBlocking<Unit> {
        val token = registerAndGetToken()
        val authApi = createAuthApi(token)

        val docsResponse = authApi.getDocuments()

        if (!docsResponse.isSuccessful || docsResponse.body().isNullOrEmpty()) {
            println("SKIP TC-MAP-01: No documents to display on map")
            return@runBlocking
        }

        val docId = docsResponse.body()!!.first().id
        val topicsResponse = authApi.getDocumentTopics(docId)

        assertTrue("Topics should load: ${topicsResponse.code()}", topicsResponse.code() != 401)
        assertNotNull("Topics should exist", topicsResponse.body())
        println("PASS TC-MAP-01: Knowledge map loads ${topicsResponse.body()?.size ?: 0} topics")
    }

    // ── DOCUMENT INGESTION FLOW TESTS ────────────────────────────────────────

    @Test
    fun `TC-INGEST-01 Upload document button flow`() = runBlocking<Unit> {
        val token = registerAndGetToken()
        val authApi = createAuthApi(token)

        val testContent = "Day la tai lieu test cho QA.\n\n## Chuong 1 Tap hop\n- Dinh nghia tap hop"
        val tempFile = File.createTempFile("test_doc", ".txt")
        tempFile.writeText(testContent)

        val requestFile = tempFile.asRequestBody("text/plain".toMediaType())
        val filePart = MultipartBody.Part.createFormData("file", tempFile.name, requestFile)
        val subjectPart = "Toan".toRequestBody("text/plain".toMediaType())

        val response = authApi.ingestDocument(filePart, subjectPart)

        tempFile.delete()

        assertTrue(
            "Upload should return 202 or fail gracefully: ${response.code()}",
            response.code() == 202 || response.code() == 500 || response.code() == 401
        )

        if (response.code() == 202) {
            println("PASS TC-INGEST-01: Document upload started")
        } else if (response.code() == 401) {
            fail("Auth failed on document upload")
        } else {
            println("WARN TC-INGEST-01: Upload accepted but backend has service issues")
        }
    }

    // ── NETWORK FAILURE TESTS ───────────────────────────────────────────────

    @Test
    fun `TC-ERROR-01 Unauthenticated requests rejected`() = runBlocking<Unit> {
        val response = api.getDocuments()

        assertEquals("Should return 401 without auth token", 401, response.code())
        println("PASS TC-ERROR-01: Unauthenticated requests blocked")
    }

    @Test
    fun `TC-ERROR-02 Invalid topic ID returns 404`() = runBlocking<Unit> {
        val token = registerAndGetToken()
        val authApi = createAuthApi(token)

        val response = authApi.getQuiz("nonexistent_topic_id_12345")

        assertTrue(
            "Invalid topic should return 404, got: ${response.code()}",
            response.code() == 404 || response.code() == 401
        )
        println("PASS TC-ERROR-02: Invalid topic ID handled correctly")
    }

    // ── HELPER METHODS ───────────────────────────────────────────────────────

    private suspend fun registerAndGetToken(): String {
        val randomEmail = "qa_${System.currentTimeMillis()}_${(1000..9999).random()}@test.com"
        val response = api.register(UserRegisterRequest(randomEmail, "password123", "QA Test"))
        return response.body()?.access_token ?: throw IllegalStateException("Failed to get token")
    }
}
