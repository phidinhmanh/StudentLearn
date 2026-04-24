package com.knowledgemap.app.data.utils

import org.junit.Assert.*
import org.junit.Test

/**
 * Unit tests for TextChunker
 * CON-S02: Truncate text <= 3000 characters per chunk
 */
class TextChunkerTest {

    // ============== Basic Chunking Tests ==============

    @Test
    fun `chunk empty text returns empty list`() {
        val chunker = TextChunker(3000)
        val result = chunker.chunk("")

        assertTrue(result.isEmpty())
    }

    @Test
    fun `chunk text smaller than max returns single chunk`() {
        val chunker = TextChunker(3000)
        val text = "Short text"

        val result = chunker.chunk(text)

        assertEquals(1, result.size)
        assertEquals("Short text", result[0])
    }

    @Test
    fun `chunk text exactly max size returns single chunk`() {
        val chunker = TextChunker(3000)
        val text = "A".repeat(3000)

        val result = chunker.chunk(text)

        assertEquals(1, result.size)
        assertEquals(3000, result[0].length)
    }

    @Test
    fun `chunk text larger than max returns multiple chunks`() {
        val chunker = TextChunker(3000)
        val text = "A".repeat(6000)

        val result = chunker.chunk(text)

        assertTrue(result.size >= 2)
        assertTrue(result.all { it.length <= 3000 })
    }

    @Test
    fun `chunk trims leading and trailing whitespace`() {
        val chunker = TextChunker(3000)
        val text = "   Content with spaces   "

        val result = chunker.chunk(text)

        assertEquals("Content with spaces", result[0])
    }

    // ============== CON-S02: Size Constraint Tests ==============

    @Test
    fun `all chunks are less than or equal to 3000 characters`() {
        val chunker = TextChunker(3000)
        val text = "Content. ".repeat(1000)

        val result = chunker.chunk(text)

        assertTrue(result.all { it.length <= 3000 })
    }

    @Test
    fun `chunk respects custom max size`() {
        val chunker = TextChunker(100)
        val text = "Word ".repeat(100)

        val result = chunker.chunk(text)

        assertTrue(result.all { it.length <= 100 })
    }

    @Test
    fun `single character repeated chunks stay under limit`() {
        val chunker = TextChunker(100)
        val text = "x".repeat(500)

        val result = chunker.chunk(text)

        assertTrue(result.all { it.length <= 100 })
    }

    // ============== Break Point Tests ==============

    @Test
    fun `chunk breaks at paragraph boundary`() {
        val chunker = TextChunker(100)
        val text = "Paragraph 1.\n\nParagraph 2. " + "A".repeat(80)

        val result = chunker.chunk(text)

        assertTrue(result.isNotEmpty())
        assertTrue(result[0].length <= 100)
    }

    @Test
    fun `chunk breaks at line boundary`() {
        val chunker = TextChunker(30)
        val text = "Line one\nLine two\nLine three"

        val result = chunker.chunk(text)

        assertTrue(result.isNotEmpty())
        assertTrue(result[0].length <= 30)
    }

    // ============== Edge Case Tests ==============

    @Test
    fun `chunk very long single word creates multiple chunks`() {
        val chunker = TextChunker(10)
        val text = "supercalifragilisticexpialidocious"

        val result = chunker.chunk(text)

        assertTrue(result.size > 1)
        assertTrue(result.all { it.length <= 10 })
    }

    @Test
    fun `chunk handles Vietnamese text`() {
        val chunker = TextChunker(3000)
        val text = "Hà Nội là thủ đô của Việt Nam. Đây là một thành phố đẹp. ".repeat(100)

        val result = chunker.chunk(text)

        assertTrue(result.isNotEmpty())
        assertTrue(result.all { it.length <= 3000 })
        assertTrue(result.joinToString("").contains("Hà Nội"))
    }

    @Test
    fun `chunk with different max sizes produces correct chunks`() {
        for (maxSize in listOf(100, 500, 1000, 3000)) {
            val chunker = TextChunker(maxSize)
            val text = "Content. ".repeat(500)

            val result = chunker.chunk(text)

            assertTrue("Failed for maxSize=$maxSize", result.all { it.length <= maxSize })
        }
    }
}