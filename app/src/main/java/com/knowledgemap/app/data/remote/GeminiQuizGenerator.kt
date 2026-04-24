package com.knowledgemap.app.data.remote

import android.content.Context
import com.knowledgemap.app.data.utils.QuizParser
import com.knowledgemap.app.domain.model.QuizQuestion
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Gemini API client for Quiz Generation
 * CON-A01: Timeout 10 seconds
 * CON-A02: Prompt với 3 components (FR-11)
 */
@Singleton
class GeminiQuizGenerator @Inject constructor(
    private val context: Context,
    private val quizParser: QuizParser
) {
    data class QuizGenerationResult(
        val success: Boolean,
        val questions: List<QuizQuestion>,
        val error: String?,
        val skippedCount: Int
    )

    suspend fun generateQuiz(
        topicName: String,
        prerequisiteTopics: List<String>,
        currentSkillLevel: Int,
        difficulty: Int = 1
    ): QuizGenerationResult = withContext(Dispatchers.IO) {
        val apiKey = ApiConfig.getGeminiApiKey(context)
        if (apiKey == null) {
            return@withContext QuizGenerationResult(
                success = false,
                questions = emptyList(),
                error = "GEMINI_API_KEY not found in local.properties",
                skippedCount = 0
            )
        }

        try {
            val prompt = buildPrompt(topicName, prerequisiteTopics, currentSkillLevel, difficulty)
            val response = callGeminiApi(prompt, apiKey)
            parseResponse(response)
        } catch (e: Exception) {
            QuizGenerationResult(
                success = false,
                questions = emptyList(),
                error = e.message ?: "Unknown error",
                skippedCount = 0
            )
        }
    }

    /**
     * Build prompt theo FR-11 và CON-A02:
     * 3 thành phần bắt buộc: topic name, KG context, skill level
     */
    private fun buildPrompt(
        topicName: String,
        prerequisiteTopics: List<String>,
        currentSkillLevel: Int,
        difficulty: Int
    ): String {
        val skillLevelText = when (currentSkillLevel) {
            0 -> "Chưa học"
            1 -> "Cần ôn"
            2 -> "Đang học"
            3 -> "Đã vững"
            else -> "Chưa học"
        }

        val prereqText = if (prerequisiteTopics.isNotEmpty()) {
            "Prerequisites: ${prerequisiteTopics.joinToString(", ")}"
        } else {
            "Prerequisites: Không có"
        }

        return """
Bạn là giáo viên Toán lớp 10. Tạo 5 câu trắc nghiệm về topic: $topicName

Context từ Knowledge Graph:
$prereqText

Skill Level hiện tại của user: $currentSkillLevel ($skillLevelText)

Yêu cầu:
- Mỗi câu có 4 đáp án (A, B, C, D)
- Độ khó phù hợp với skill level
- Trả lời JSON array theo format sau:

[
  {
    "q": "Câu hỏi",
    "opts": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
    "correct": 0,
    "explain": "Giải thích đáp án đúng"
  },
  ...
]
        """.trimIndent()
    }

    private fun callGeminiApi(prompt: String, apiKey: String): String {
        val url = URL("${ApiConfig.getGeminiUrl()}?key=$apiKey")
        val connection = url.openConnection() as HttpURLConnection

        try {
            connection.requestMethod = "POST"
            connection.connectTimeout = ApiConfig.TIMEOUT_MS.toInt()
            connection.readTimeout = ApiConfig.TIMEOUT_MS.toInt()
            connection.setRequestProperty("Content-Type", "application/json")

            connection.doOutput = true
            val body = buildRequestBody(prompt)

            OutputStreamWriter(connection.outputStream).use { writer ->
                writer.write(body)
                writer.flush()
            }

            val responseCode = connection.responseCode
            if (responseCode != 200) {
                throw Exception("API error: $responseCode")
            }

            return connection.inputStream.bufferedReader().readText()
        } finally {
            connection.disconnect()
        }
    }

    private fun buildRequestBody(prompt: String): String {
        return JSONObject().apply {
            put("contents", org.json.JSONArray().put(
                JSONObject().put("parts", org.json.JSONArray().put(
                    JSONObject().put("text", prompt)
                ))
            ))
            put("generationConfig", JSONObject().apply {
                put("temperature", 0.7)
                put("maxOutputTokens", 2048)
                put("topP", 0.9)
            })
        }.toString()
    }

    private fun parseResponse(response: String): QuizGenerationResult {
        val jsonResponse = JSONObject(response)
        val candidates = jsonResponse.optJSONArray("candidates")

        if (candidates == null || candidates.length() == 0) {
            return QuizGenerationResult(
                success = false,
                questions = emptyList(),
                error = "No response from Gemini",
                skippedCount = 0
            )
        }

        val content = candidates.getJSONObject(0)
            .optJSONObject("content")
            ?.optJSONArray("parts")
            ?.optJSONObject(0)
            ?.optString("text", "")

        if (content.isNullOrEmpty()) {
            return QuizGenerationResult(
                success = false,
                questions = emptyList(),
                error = "Empty response from Gemini",
                skippedCount = 0
            )
        }

        val result = quizParser.parse(content)

        return QuizGenerationResult(
            success = result.questions.isNotEmpty(),
            questions = result.questions,
            error = if (result.errors.isNotEmpty() && result.questions.isEmpty()) {
                result.errors.joinToString("; ")
            } else null,
            skippedCount = result.skippedCount
        )
    }
}