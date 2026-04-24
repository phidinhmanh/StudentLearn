package com.knowledgemap.app.data.utils

import javax.inject.Inject
import javax.inject.Singleton

/**
 * Text chunker for Document Ingestion
 * CON-S02: Truncate text ≤ 3000 characters per chunk
 */
@Singleton
class TextChunker @Inject constructor(
    private val maxChunkSize: Int = 3000
) {
    fun chunk(text: String): List<String> {
        if (text.isEmpty()) return emptyList()

        val trimmedText = text.trim()
        if (trimmedText.length <= maxChunkSize) {
            return listOf(trimmedText)
        }

        val chunks = mutableListOf<String>()
        var remaining = trimmedText

        while (remaining.isNotEmpty()) {
            val chunkSize = minOf(maxChunkSize, remaining.length)
            val chunk = remaining.substring(0, chunkSize)

            // Try to break at sentence or paragraph boundary
            val breakIndex = findBreakPoint(chunk)
            val (actualChunk, charsUsed) = if (breakIndex > maxChunkSize / 2 && breakIndex < chunkSize) {
                chunk.substring(0, breakIndex) to breakIndex
            } else {
                chunk to chunkSize
            }

            chunks.add(actualChunk.trim())
            remaining = if (charsUsed < remaining.length) {
                remaining.substring(charsUsed).trim()
            } else {
                ""
            }
        }

        return chunks
    }

    private fun findBreakPoint(text: String): Int {
        // Try to break at paragraph (double newline)
        val paragraphBreak = text.lastIndexOf("\n\n")
        if (paragraphBreak > maxChunkSize / 2 && paragraphBreak < text.length) return paragraphBreak

        // Try to break at sentence (period, question mark, exclamation)
        val sentenceBreaks = listOf(".\n", ".\r", "!\n", "!\r", "?\n", "?\r")
        for (separator in sentenceBreaks) {
            val idx = text.lastIndexOf(separator)
            if (idx > maxChunkSize / 2 && idx + 1 < text.length) return idx + 1
        }

        // Try to break at sentence (full stop in Vietnamese)
        val fullStopIdx = text.lastIndexOf(".")
        if (fullStopIdx > maxChunkSize / 2 && fullStopIdx + 1 < text.length) return fullStopIdx + 1

        // Try to break at line
        val lineBreak = text.lastIndexOf("\n")
        if (lineBreak > maxChunkSize / 2 && lineBreak + 1 < text.length) return lineBreak + 1

        // Fallback to word boundary
        val searchEnd = minOf(text.length - 1, maxChunkSize - 1)
        val wordBreak = text.lastIndexOf(" ", searchEnd)
        return if (wordBreak > maxChunkSize / 2) wordBreak else maxChunkSize
    }
}