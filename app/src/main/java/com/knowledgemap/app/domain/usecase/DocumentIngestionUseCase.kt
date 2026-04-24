package com.knowledgemap.app.domain.usecase

import com.knowledgemap.app.data.remote.GeminiGraphExtractor
import com.knowledgemap.app.data.utils.TextChunker
import com.knowledgemap.app.domain.model.TopicEdge
import com.knowledgemap.app.domain.model.TopicNode
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Document Ingestion UseCase - orchestrates KG extraction
 * CON-S02: Truncate text ≤ 3000 chars per chunk
 * CON-A01: Timeout 10 seconds
 */
@Singleton
class DocumentIngestionUseCase @Inject constructor(
    private val textChunker: TextChunker,
    private val graphExtractor: GeminiGraphExtractor
) {
    data class IngestionResult(
        val success: Boolean,
        val nodes: List<TopicNode>,
        val edges: List<TopicEdge>,
        val error: String?,
        val chunksProcessed: Int
    )

    suspend fun ingest(documentText: String, chapter: String = "unknown"): IngestionResult {
        // CON-S02: Chunk text ≤ 3000 chars
        val chunks = textChunker.chunk(documentText)

        if (chunks.isEmpty()) {
            return IngestionResult(
                success = false,
                nodes = emptyList(),
                edges = emptyList(),
                error = "Empty document",
                chunksProcessed = 0
            )
        }

        val allNodes = mutableListOf<TopicNode>()
        val allEdges = mutableListOf<TopicEdge>()
        val errors = mutableListOf<String>()

        // Process each chunk
        for ((index, chunk) in chunks.withIndex()) {
            val result = graphExtractor.extract(chunk, chapter)

            if (result.success) {
                // Deduplicate nodes by ID
                val existingIds = allNodes.map { it.id }.toSet()
                result.nodes.filter { it.id !in existingIds }.let { newNodes ->
                    allNodes.addAll(newNodes)
                }

                // Deduplicate edges
                val existingEdges = allEdges.map { "${it.fromId}-${it.toId}-${it.relation}" }.toSet()
                result.edges.filter { "${it.fromId}-${it.toId}-${it.relation}" !in existingEdges }.let { newEdges ->
                    allEdges.addAll(newEdges)
                }
            } else {
                result.error?.let { errors.add("Chunk ${index + 1}: $it") }
            }
        }

        return IngestionResult(
            success = allNodes.isNotEmpty(),
            nodes = allNodes,
            edges = allEdges,
            error = if (errors.isNotEmpty()) errors.joinToString("; ") else null,
            chunksProcessed = chunks.size
        )
    }
}