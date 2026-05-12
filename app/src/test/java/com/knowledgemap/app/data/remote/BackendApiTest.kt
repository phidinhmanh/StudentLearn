package com.knowledgemap.app.data.remote

import com.knowledgemap.app.data.remote.dto.UserLoginRequest
import kotlinx.coroutines.runBlocking
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Integration test for Backend API.
 * NOTE: Requires backend server running at [ApiConfig.BACKEND_BASE_URL]
 */
class BackendApiTest {

    private lateinit var api: StudentLearnApi

    @Before
    fun setup() {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }

        val client = OkHttpClient.Builder()
            .addInterceptor(logging)
            .connectTimeout(5, TimeUnit.SECONDS)
            .readTimeout(5, TimeUnit.SECONDS)
            .build()

        val retrofit = Retrofit.Builder()
            .baseUrl(ApiConfig.BACKEND_BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

        api = retrofit.create(StudentLearnApi::class.java)
    }

    @Test
    fun `health check returns ok`() = runBlocking {
        try {
            val response = api.healthCheck()
            assertTrue("Health check failed: ${response.errorBody()?.string()}", response.isSuccessful)
            val body = response.body()
            assertNotNull(body)
            assertTrue(body?.status == "ok" || body?.status == "degraded")
        } catch (e: Exception) {
            System.err.println("Backend unreachable at ${ApiConfig.BACKEND_BASE_URL}: ${e.message}")
            // Don't fail the build if backend is just offline for this test
        }
    }

    @Test
    fun `full auth and data flow test`() = runBlocking {
        try {
            // 1. Register (Randomize email to avoid conflict)
            val random = (1000..9999).random()
            val email = "test_$random@example.com"
            val registerReq = com.knowledgemap.app.data.remote.dto.UserRegisterRequest(email, "password123", "Test User")
            val regResponse = api.register(registerReq)

            if (regResponse.code() == 503) {
                System.err.println("User service unavailable, skipping auth flow test")
                return@runBlocking
            }

            assertTrue("Register failed: ${regResponse.errorBody()?.string()}", regResponse.isSuccessful)
            val token = regResponse.body()?.access_token
            assertNotNull("Token should not be null", token)

            // Create an authenticated API instance
            val authClient = OkHttpClient.Builder()
                .addInterceptor { chain ->
                    val req = chain.request().newBuilder()
                        .addHeader("Authorization", "Bearer $token")
                        .build()
                    chain.proceed(req)
                }
                .build()

            val authApi = Retrofit.Builder()
                .baseUrl(ApiConfig.BACKEND_BASE_URL)
                .client(authClient)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .create(StudentLearnApi::class.java)

            // 2. Get Documents (Should be empty for new user)
            val docsResponse = authApi.getDocuments()
            assertTrue(docsResponse.isSuccessful)
            assertNotNull(docsResponse.body())

            // 3. Health check again with auth
            val healthAuth = authApi.healthCheck()
            assertTrue(healthAuth.isSuccessful)

            // 4. Test Quiz endpoint with a common ID (may 404 if no data, but should not 401)
            val quizResponse = authApi.getQuiz("ch1_tap_hop")
            // 200 or 404 is acceptable logic-wise (if data not seeded), but 401 is failure
            assertTrue("Auth failed on quiz: ${quizResponse.code()}", quizResponse.code() != 401)

            // 5. Test Progress update
            val userId = "test_user_id" // In real flow we extract from token, but here we just test endpoint reachability
            val progressReq = com.knowledgemap.app.data.remote.dto.ProgressUpdateRequest(skill_level = 2)
            val progressResponse = authApi.updateProgress(userId, "ch1_tap_hop", progressReq)
            assertTrue("Progress update failed: ${progressResponse.code()}", progressResponse.code() != 401)

        } catch (e: Exception) {
            System.err.println("Flow test failed: ${e.message}")
        }
    }

    @Test
    fun `login with invalid credentials returns 401`() = runBlocking {
        try {
            val request = UserLoginRequest("invalid@example.com", "wrongpassword")
            val response = api.login(request)
            assertEquals(401, response.code())
        } catch (e: Exception) {
            System.err.println("Backend unreachable: ${e.message}")
        }
    }

    @Test
    fun `get documents without token returns 401`() = runBlocking {
        try {
            val response = api.getDocuments()
            assertEquals(401, response.code())
        } catch (e: Exception) {
            System.err.println("Backend unreachable: ${e.message}")
        }
    }
}
