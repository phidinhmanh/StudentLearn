package com.knowledgemap.app.data.utils

import com.knowledgemap.app.domain.model.QuizQuestion
import org.json.JSONArray
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Quiz parser - validates and parses Gemini quiz JSON
 * CON-A05: Validate 4 fields, skip invalid questions
 */
@Singleton
class QuizParser @Inject constructor() {

    data class ParseResult(
        val questions: List<QuizQuestion>,
        val skippedCount: Int,
        val errors: List<String>
    )

    fun parse(jsonString: String): ParseResult {
        val questions = mutableListOf<QuizQuestion>()
        val errors = mutableListOf<String>()
        var skippedCount = 0

        try {
            // Clean markdown code blocks if present
            val cleanJson = jsonString
                .replace("```json", "")
                .replace("```", "")
                .trim()

            val jsonArray = JSONArray(cleanJson)

            for (i in 0 until jsonArray.length()) {
                val obj = jsonArray.getJSONObject(i)

                val question = obj.optString("q", "")
                val optionsArray = obj.optJSONArray("opts")
                val correctIndex = obj.optInt("correct", -1)
                val explanation = obj.optString("explain", "")

                // Validate required fields (CON-A05)
                if (question.isEmpty()) {
                    errors.add("Question at index $i missing 'q'")
                    skippedCount++
                    continue
                }

                if (optionsArray == null || optionsArray.length() != 4) {
                    errors.add("Question '$question' invalid 'opts' (must be 4 options)")
                    skippedCount++
                    continue
                }

                if (correctIndex !in 0..3) {
                    errors.add("Question '$question' invalid 'correct': $correctIndex (must be 0-3)")
                    skippedCount++
                    continue
                }

                // Parse options
                val options = mutableListOf<String>()
                var validOptions = true
                for (j in 0 until 4) {
                    val option = optionsArray.optString(j, "")
                    if (option.isEmpty()) {
                        errors.add("Question '$question' option ${j + 1} is empty")
                        skippedCount++
                        validOptions = false
                        break
                    }
                    options.add(option)
                }

                if (!validOptions) continue

                // All fields valid - create question
                try {
                    questions.add(
                        QuizQuestion(
                            question = question,
                            options = options,
                            correctIndex = correctIndex,
                            explanation = explanation
                        )
                    )
                } catch (e: Exception) {
                    errors.add("Failed to create question '$question': ${e.message}")
                    skippedCount++
                }
            }

        } catch (e: Exception) {
            errors.add("JSON parse error: ${e.message}")
        }

        return ParseResult(
            questions = questions,
            skippedCount = skippedCount,
            errors = errors
        )
    }
}