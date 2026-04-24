package com.knowledgemap.app.data.utils

import com.knowledgemap.app.domain.model.EdgeRelation
import com.knowledgemap.app.domain.model.TopicEdge
import com.knowledgemap.app.domain.model.TopicNode
import org.json.JSONArray
import org.json.JSONObject
import javax.inject.Inject
import javax.inject.Singleton

/**
 * Graph validator - validates KG extraction JSON
 * CON-A05: Validate 4 fields per question
 */
@Singleton
class GraphValidator @Inject constructor() {

    data class ValidationResult(
        val isValid: Boolean,
        val nodes: List<TopicNode>,
        val edges: List<TopicEdge>,
        val errors: List<String>
    )

    fun validate(jsonString: String, chapter: String = "unknown"): ValidationResult {
        val errors = mutableListOf<String>()
        val nodes = mutableListOf<TopicNode>()
        val edges = mutableListOf<TopicEdge>()
        val seenNodeIds = mutableSetOf<String>()

        try {
            val jsonArray = JSONArray(jsonString)

            for (i in 0 until jsonArray.length()) {
                val obj = jsonArray.getJSONObject(i)

                // Validate required fields (CON-G02)
                val id = obj.optString("id", "")
                val name = obj.optString("name", "")
                val desc = obj.optString("desc", "")
                val difficulty = obj.optInt("difficulty", 0)

                if (id.isEmpty()) {
                    errors.add("Node at index $i missing 'id'")
                    continue
                }
                if (name.isEmpty()) {
                    errors.add("Node '$id' missing 'name'")
                    continue
                }
                if (difficulty !in 1..3) {
                    errors.add("Node '$id' invalid difficulty: $difficulty (must be 1-3)")
                    continue
                }

                // Create node
                val node = TopicNode(
                    id = id,
                    name = name,
                    desc = desc.take(100), // CON-G02: ≤100 chars
                    difficulty = difficulty,
                    chapter = chapter,
                    skillLevel = 0,
                    lastAssessed = null
                )
                nodes.add(node)

                // Parse prerequisites as edges
                val prereqArray = obj.optJSONArray("prereq")
                if (prereqArray != null) {
                    for (j in 0 until prereqArray.length()) {
                        val prereqId = prereqArray.getString(j)
                        if (prereqId.isNotEmpty()) {
                            edges.add(
                                TopicEdge(
                                    fromId = prereqId,
                                    toId = id,
                                    relation = EdgeRelation.PREREQUISITE,
                                    weight = 1.0f
                                )
                            )
                        }
                    }
                }

                // Parse optional relations
                val sequenceOf = obj.optJSONArray("sequenceOf")
                if (sequenceOf != null) {
                    for (j in 0 until sequenceOf.length()) {
                        edges.add(
                            TopicEdge(
                                fromId = sequenceOf.getString(j),
                                toId = id,
                                relation = EdgeRelation.SEQUENCE_OF,
                                weight = 1.0f
                            )
                        )
                    }
                }

                val relatedTo = obj.optJSONArray("relatedTo")
                if (relatedTo != null) {
                    for (j in 0 until relatedTo.length()) {
                        edges.add(
                            TopicEdge(
                                fromId = relatedTo.getString(j),
                                toId = id,
                                relation = EdgeRelation.RELATED_TO,
                                weight = 1.0f
                            )
                        )
                    }
                }
            }

        } catch (e: Exception) {
            errors.add("JSON parse error: ${e.message}")
        }

        return ValidationResult(
            isValid = errors.isEmpty() && nodes.isNotEmpty(),
            nodes = nodes,
            edges = edges,
            errors = errors
        )
    }
}