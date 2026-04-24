package com.knowledgemap.app.data.utils

import org.junit.Assert.*
import org.junit.Test

/**
 * Unit tests for GraphValidator
 * CON-G02: Node has all required fields
 */
class GraphValidatorTest {

    private val validator = GraphValidator()

    @Test
    fun `skip node missing id returns empty`() {
        val json = "[{\"name\":\"No ID\",\"desc\":\"Desc\",\"difficulty\":1}]"
        val result = validator.validate(json)
        assertFalse(result.isValid)
        assertEquals(0, result.nodes.size)
        assertTrue(result.errors.isNotEmpty())
    }

    @Test
    fun `skip node missing name returns empty`() {
        val json = "[{\"id\":\"some-id\",\"desc\":\"Desc\",\"difficulty\":1}]"
        val result = validator.validate(json)
        assertFalse(result.isValid)
        assertEquals(0, result.nodes.size)
        assertTrue(result.errors.isNotEmpty())
    }

    @Test
    fun `skip node with invalid difficulty`() {
        val json = "[{\"id\":\"test-id\",\"name\":\"Test\",\"desc\":\"Desc\",\"difficulty\":5}]"
        val result = validator.validate(json)
        assertFalse(result.isValid)
        assertEquals(0, result.nodes.size)
        assertTrue(result.errors.isNotEmpty())
    }

    @Test
    fun `validate with empty array returns invalid`() {
        val json = "[]"
        val result = validator.validate(json)
        assertFalse(result.isValid)
        assertEquals(0, result.nodes.size)
    }

    @Test
    fun `validate with invalid JSON returns error`() {
        val json = "not valid json"
        val result = validator.validate(json)
        assertFalse(result.isValid)
        assertTrue(result.errors.isNotEmpty())
    }
}