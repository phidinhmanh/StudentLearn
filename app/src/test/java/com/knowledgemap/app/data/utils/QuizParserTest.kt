package com.knowledgemap.app.data.utils

import org.junit.Assert.*
import org.junit.Test

/**
 * Unit tests for QuizParser
 * CON-A05: Validate 4 fields, skip invalid questions
 */
class QuizParserTest {

    private val parser = QuizParser()

    @Test
    fun `parse empty JSON array returns empty list`() {
        val json = "[]"
        val result = parser.parse(json)
        assertEquals(0, result.questions.size)
        assertEquals(0, result.skippedCount)
    }

    @Test
    fun `parse invalid JSON returns empty with error`() {
        val json = "invalid json"
        val result = parser.parse(json)
        assertEquals(0, result.questions.size)
        assertTrue(result.errors.isNotEmpty())
    }
}