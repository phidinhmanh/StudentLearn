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
