package com.knowledgemap.app.data.remote

import android.content.Context
import java.util.Properties

object ApiConfig {
    private const val GEMINI_MODEL = "gemini-2.0-flash"
    private const val GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/"

    const val BACKEND_BASE_URL = "https://studentlearn-api3.onrender.com/"
    const val TIMEOUT_MS = 10_000L

    fun getGeminiApiKey(context: Context): String? {
        return try {
            val localProperties = Properties()
            val file = java.io.File("local.properties")
            if (file.exists()) {
                file.inputStream().use { localProperties.load(it) }
                localProperties.getProperty("GEMINI_API_KEY")
            } else null
        } catch (e: Exception) {
            null
        }
    }

    fun getGeminiModel(): String = GEMINI_MODEL

    fun getGeminiUrl(): String = "$GEMINI_BASE_URL$GEMINI_MODEL:generateContent"
}