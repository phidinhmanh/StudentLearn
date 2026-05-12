"""Integration tests for graph extractor."""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock

from app.services.document_parser import TextChunk
from app.services.graph_extractor import _deduplicate_graph, extract_knowledge_graph


class TestDeduplicateGraph:
    """Tests for graph deduplication logic."""

    def test_removes_duplicate_entities_by_name(self):
        """Should remove duplicate entities case-insensitively."""
        entities = [
            {"name": "Hàm số bậc hai", "type": "concept"},
            {"name": "hàm số bậc hai", "type": "formula"},  # Duplicate
            {"name": "Parabol", "type": "concept"},
        ]

        deduped_entities, _ = _deduplicate_graph(entities, [])
        names = [e["name"] for e in deduped_entities]

        assert len(deduped_entities) == 2
        assert "Hàm số bậc hai" in names
        assert "Parabol" in names

    def test_merges_descriptions_on_duplicate(self):
        """Should merge description from duplicate entity."""
        entities = [
            {"name": "Hàm số", "type": "concept", "description": "Dạng y = ax^2"},
            {"name": "hàm số", "type": "concept"},  # No description
        ]

        deduped_entities, _ = _deduplicate_graph(entities, [])
        assert len(deduped_entities) == 1
        assert deduped_entities[0]["description"] == "Dạng y = ax^2"

    def test_ignores_empty_name_entities(self):
        """Should ignore entities with empty names."""
        entities = [
            {"name": "Valid Topic", "type": "concept"},
            {"name": "", "type": "concept"},
            {"name": "   ", "type": "concept"},
        ]

        deduped_entities, _ = _deduplicate_graph(entities, [])
        assert len(deduped_entities) == 1

    def test_removes_duplicate_edges(self):
        """Should remove duplicate edges by (from, to, relation)."""
        edges = [
            {"from_name": "A", "to_name": "B", "relation": "prerequisite", "weight": 1.0},
            {"from_name": "A", "to_name": "B", "relation": "prerequisite", "weight": 1.0},  # Duplicate
            {"from_name": "B", "to_name": "C", "relation": "relatedTo", "weight": 1.0},
        ]

        _, deduped_edges = _deduplicate_graph([], edges)

        assert len(deduped_edges) == 2

    def test_merges_edge_weights(self):
        """Should merge weights for duplicate edges."""
        edges = [
            {"from_name": "A", "to_name": "B", "relation": "prerequisite", "weight": 1.0},
            {"from_name": "a", "to_name": "b", "relation": "prerequisite", "weight": 2.0},  # Same edge
        ]

        _, deduped_edges = _deduplicate_graph([], edges)

        assert len(deduped_edges) == 1
        assert deduped_edges[0]["weight"] == 3.0  # 1.0 + 2.0

    def test_ignores_edges_without_endpoints(self):
        """Should ignore edges with missing from/to."""
        edges = [
            {"from_name": "A", "to_name": "B", "relation": "prerequisite"},
            {"from_name": "", "to_name": "B", "relation": "relatedTo"},  # Missing from
            {"from_name": "A", "to_name": "", "relation": "relatedTo"},  # Missing to
        ]

        _, deduped_edges = _deduplicate_graph([], edges)

        assert len(deduped_edges) == 1

    def test_handles_empty_inputs(self):
        """Should handle empty entity and relation lists."""
        entities, relations = _deduplicate_graph([], [])
        assert entities == []
        assert relations == []

    def test_preserves_first_entity_attributes(self):
        """Should keep first entity's attributes."""
        entities = [
            {"name": "Topic", "type": "formula", "difficulty": "hard"},
            {"name": "topic", "type": "concept", "difficulty": "easy"},
        ]

        deduped_entities, _ = _deduplicate_graph(entities, [])

        assert deduped_entities[0]["type"] == "formula"
        assert deduped_entities[0]["difficulty"] == "hard"

    def test_handles_different_relation_types(self):
        """Should keep edges with different relation types."""
        edges = [
            {"from_name": "A", "to_name": "B", "relation": "prerequisite"},
            {"from_name": "A", "to_name": "B", "relation": "relatedTo"},  # Different type
        ]

        _, deduped_edges = _deduplicate_graph([], edges)

        assert len(deduped_edges) == 2


class TestExtractKnowledgeGraph:
    """Tests for main extraction pipeline."""

    @pytest.mark.asyncio
    @patch("app.services.graph_extractor.get_graph_service")
    @patch("app.services.graph_extractor.get_llm")
    async def test_extracts_from_chunks(self, mock_get_llm, mock_get_graph, sample_chunks_for_extraction):
        """Should process chunks and extract entities."""
        # Mock LLM response
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(
            content='{"nodes": [{"name": "Test Topic", "type": "concept"}], "edges": []}'
        )
        mock_get_llm.return_value = mock_llm

        # Mock Graph service
        mock_graph = MagicMock()
        mock_graph.batch_upsert_topics.return_value = [{"name": "Test Topic"}]
        mock_graph.batch_upsert_edges.return_value = 0
        mock_get_graph.return_value = mock_graph

        result = await extract_knowledge_graph(
            chunks=sample_chunks_for_extraction,
            doc_id="doc-123",
            subject="toan"
        )

        assert "topics_created" in result
        assert "edges_created" in result

    @pytest.mark.asyncio
    @patch("app.services.graph_extractor.get_graph_service")
    @patch("app.services.graph_extractor.get_llm")
    async def test_handles_llm_json_error(self, mock_get_llm, mock_get_graph):
        """Should handle invalid JSON from LLM."""
        # Mock LLM with invalid JSON
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content="Not valid JSON")
        mock_get_llm.return_value = mock_llm

        mock_graph = MagicMock()
        mock_get_graph.return_value = mock_graph

        chunks = [TextChunk(text="Some content", page_number=1, char_count=50)]

        result = await extract_knowledge_graph(chunks, "doc-123")

        # Should not crash, returns empty results
        assert "topics_created" in result
        assert result["topics_created"] == 0

    @pytest.mark.asyncio
    @patch("app.services.graph_extractor.get_graph_service")
    @patch("app.services.graph_extractor.get_llm")
    async def test_processes_in_batches(self, mock_get_llm, mock_get_graph):
        """Should process chunks, grouping them into windows by 15K chars."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(
            content='{"nodes": [], "edges": []}'
        )
        mock_get_llm.return_value = mock_llm

        mock_graph = MagicMock()
        mock_graph.batch_upsert_topics.return_value = []
        mock_graph.batch_upsert_edges.return_value = 0
        mock_get_graph.return_value = mock_graph

        # 6 small chunks – they fit into a single window (<15K chars).
        chunks = [
            TextChunk(text=f"Chunk {i}", page_number=i, char_count=50)
            for i in range(6)
        ]

        await extract_knowledge_graph(chunks, "doc-123")

        # All chunks fit in one window, so LLM.invoke is called once.
        assert mock_llm.invoke.call_count == 1

    @pytest.mark.asyncio
    @patch("app.services.graph_extractor.get_graph_service")
    @patch("app.services.graph_extractor.get_llm")
    async def test_creates_edges_for_existing_topics(self, mock_get_llm, mock_get_graph):
        """Should only create edges when both topics exist."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content=(
            '{"nodes": [{"name": "A"}, {"name": "B"}], '
            '"edges": [{"from_name": "A", "to_name": "B", "relation": "prerequisite"}]}'
        ))
        mock_get_llm.return_value = mock_llm

        mock_graph = MagicMock()
        mock_graph.batch_upsert_topics.side_effect = [["id-a"], ["id-b"]]
        mock_graph.batch_upsert_edges.return_value = True
        mock_get_graph.return_value = mock_graph

        chunks = [TextChunk(text="A is related to B", page_number=1, char_count=50)]
        await extract_knowledge_graph(chunks, "doc-123")

        # upsert_edge should be called
        assert mock_graph.batch_upsert_edges.called

    @pytest.mark.asyncio
    @patch("app.services.graph_extractor.get_graph_service")
    @patch("app.services.graph_extractor.get_llm")
    async def test_skips_edges_for_missing_topics(self, mock_get_llm, mock_get_graph):
        """Should not create edges when topic doesn't exist."""
        mock_llm = MagicMock()
        mock_llm.invoke.return_value = MagicMock(content=(
            '{"nodes": [{"name": "A"}], '
            '"edges": [{"from_name": "A", "to_name": "Missing", "relation": "relatedTo"}]}'
        ))
        mock_get_llm.return_value = mock_llm

        mock_graph = MagicMock()
        mock_graph.batch_upsert_topics.return_value = ["id-a"]
        mock_get_graph.return_value = mock_graph

        chunks = [TextChunk(text="A relates to Missing", page_number=1, char_count=50)]
        await extract_knowledge_graph(chunks, "doc-123")

        # upsert_edge should NOT be called because "Missing" not in name_to_id
        mock_graph.batch_upsert_edges.assert_not_called

    @pytest.mark.asyncio
    @patch("app.services.graph_extractor.get_graph_service")
    @patch("app.services.graph_extractor.get_llm")
    async def test_empty_chunks(self, mock_get_llm, mock_get_graph):
        """Should handle empty chunks list."""
        mock_graph = MagicMock()
        mock_graph.batch_upsert_topics.return_value = []
        mock_graph.batch_upsert_edges.return_value = 0
        mock_get_graph.return_value = mock_graph

        result = await extract_knowledge_graph([], "doc-123")

        assert result["topics_created"] == 0
        assert result["edges_created"] == 0


class TestBatchProcessing:
    """Tests for batch processing edge cases."""

    def test_single_chunk(self):
        """Should handle single chunk."""
        entities = [{"name": "Topic", "type": "concept"}]
        relations = []

        deduped_entities, deduped_relations = _deduplicate_graph(entities, relations)

        assert len(deduped_entities) == 1
        assert len(deduped_relations) == 0

    def test_multiple_same_topic(self):
        """Should dedupe when same topic appears multiple times."""
        entities = [
            {"name": "Topic A", "type": "concept"},
            {"name": "Topic A", "type": "concept"},
            {"name": "topic a", "type": "concept"},
            {"name": "Topic B", "type": "concept"},
        ]

        deduped, _ = _deduplicate_graph(entities, [])

        assert len(deduped) == 2

    def test_complex_relations(self):
        """Should handle complex multi-level relations."""
        edges = [
            {"from_name": "A", "to_name": "B", "relation": "prerequisite"},
            {"from_name": "B", "to_name": "C", "relation": "prerequisite"},
            {"from_name": "C", "to_name": "D", "relation": "sequenceOf"},
            {"from_name": "A", "to_name": "D", "relation": "relatedTo"},
        ]

        _, deduped = _deduplicate_graph([], edges)

        assert len(deduped) == 4