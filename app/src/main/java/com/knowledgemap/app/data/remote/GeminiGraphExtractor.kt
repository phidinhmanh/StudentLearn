package com.knowledgemap.app.data.remote

import android.content.Context
import com.knowledgemap.app.data.utils.GraphValidator
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import org.json.JSONObject
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Gemini API client for Knowledge Graph extraction
 * CON-A01: Timeout 10 seconds
 * CON-A02: Prompt with 3 components
 */
@Singleton
class GeminiGraphExtractor @Inject constructor(
    private val context: Context,
    private val validator: GraphValidator
) {
    data class ExtractionResult(
        val success: Boolean,
        val nodes: List<com.knowledgemap.app.domain.model.TopicNode>,
        val edges: List<com.knowledgemap.app.domain.model.TopicEdge>,
        val error: String?
    )

    suspend fun extract(text: String, chapter: String = "unknown"): ExtractionResult = withContext(Dispatchers.IO) {
        val apiKey = ApiConfig.getGeminiApiKey(context)
        if (apiKey == null) {
            return@withContext ExtractionResult(
                success = false,
                nodes = emptyList(),
                edges = emptyList(),
                error = "GEMINI_API_KEY not found in local.properties"
            )
        }

        try {
            val prompt = buildPrompt(text)
            val response = callGeminiApi(prompt, apiKey)
            parseResponse(response, chapter)
        } catch (e: Exception) {
            ExtractionResult(
                success = false,
                nodes = emptyList(),
                edges = emptyList(),
                error = e.message ?: "Unknown error"
            )
        }
    }

    private fun buildPrompt(text: String): String {
        return """
Phân tích văn bản sau và trích xuất Knowledge Graph về Toán lớp 10:

$text

Trả lời JSON array các topic nodes:

[
  {
    "id": "topic_unique_id",
    "name": "Tên topic (tiếng Việt)",
    "desc": "Mô tả ngắn (≤100 ký tự)",
    "difficulty": 1,
    "prereq": ["id_topic_cần_học_trước"]
  }
]

Các loại quan hệ:
- prerequisite: Phải học trước (A prerequisite của B = A → B)
- sequenceOf: Cùng chương, thứ tự
- relatedTo: Liên quan nhưng không bắt buộc

Chỉ trả JSON, không giải thích.
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

    private fun parseResponse(response: String, chapter: String): ExtractionResult {
        // Extract JSON from Gemini response
        val jsonResponse = JSONObject(response)
        val candidates = jsonResponse.optJSONArray("candidates")

        if (candidates == null || candidates.length() == 0) {
            return ExtractionResult(
                success = false,
                nodes = emptyList(),
                edges = emptyList(),
                error = "No response from Gemini"
            )
        }

        val content = candidates.getJSONObject(0)
            .optJSONObject("content")
            ?.optJSONArray("parts")
            ?.optJSONObject(0)
            ?.optString("text", "")

        if (content.isNullOrEmpty()) {
            return ExtractionResult(
                success = false,
                nodes = emptyList(),
                edges = emptyList(),
                error = "Empty response from Gemini"
            )
        }

        // Parse JSON array (may be wrapped in markdown code block)
        val cleanJson = content
            .replace("```json", "")
            .replace("```", "")
            .trim()

        val result = validator.validate(cleanJson, chapter)

        return ExtractionResult(
            success = result.isValid,
            nodes = result.nodes,
            edges = result.edges,
            error = if (result.errors.isNotEmpty()) result.errors.joinToString("; ") else null
        )
    }
}