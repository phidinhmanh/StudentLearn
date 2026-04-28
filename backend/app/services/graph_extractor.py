import json
import asyncio
import logging
from typing import List, Dict, Any
from app.services.factory import get_graph_service
from app.services.document_parser import TextChunk, chunk_for_embedding
from app.utils.gemini_client import get_llm
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


async def extract_knowledge_graph(
    chunks: List[TextChunk],
    doc_id: str,
    subject: str = "general",
) -> Dict[str, Any]:
    """Main GraphRAG extraction pipeline"""
    service = get_graph_service()

    # If using Cognee, we can leverage its automated pipeline
    if settings.graph_provider.lower() == "cognee":
        try:
            full_text = "\n\n".join([c.text for c in chunks])
            # cognee_service has an ingest_text method
            if hasattr(service, "ingest_text"):
                await service.ingest_text(full_text, dataset_name=f"doc_{doc_id}")
        except Exception as e:
            logger.error(f"Cognee ingestion failed: {e}")
            # Fall back to manual extraction if cognee fails or continue

    # Regroup chunks into larger context windows (e.g. 4000 chars) to reduce LLM calls
    windows = []
    current_window = []
    current_size = 0
    for chunk in chunks:
        chunk_text = chunk.text.strip()
        if not chunk_text:
            continue
        if current_size + len(chunk_text) > 15000 and current_window:
            windows.append("\n\n".join(current_window))
            current_window = [chunk_text]
            current_size = len(chunk_text)
        else:
            current_window.append(chunk_text)
            current_size += len(chunk_text)
    if current_window:
        windows.append("\n\n".join(current_window))

    # Process windows concurrently with semaphore
    semaphore = asyncio.Semaphore(3)  # Limit to 3 concurrent LLM calls
    all_entities = []
    all_relations = []

    async def sem_extract(text):
        async with semaphore:
            try:
                # Add 180s timeout per large window
                return await asyncio.wait_for(_extract_from_batch([text], subject), timeout=300.0)
            except asyncio.TimeoutError:
                logger.error("LLM window extraction timed out")
                return {"nodes": [], "edges": []}
            except Exception:
                logger.exception("Error in window extraction")
                return {"nodes": [], "edges": []}

    tasks = [sem_extract(w) for w in windows]
    
    # Run all batches in parallel (limited by semaphore)
    try:
        results = await asyncio.gather(*tasks)
    except Exception:
        logger.exception("Knowledge graph extraction failed for doc_id=%s", doc_id)
        raise
    
    for result in results:
        all_entities.extend(result.get("nodes", []))
        all_relations.extend(result.get("edges", []))

    # Phase 2: Deduplication
    entities, relations = _deduplicate_graph(all_entities, all_relations)

    # Phase 3: Insert into service using batch methods
    inserted_topics = await service.batch_upsert_topics(entities, doc_id)
    
    # Insert edges in batch
    # Note: CogneeService might not implement batch_upsert_edges yet, 
    # but we should ensure the base interface or service handles it.
    inserted_edges_count = 0
    if hasattr(service, "batch_upsert_edges"):
        inserted_edges_count = await service.batch_upsert_edges(relations)

    return {
        "topics_created": len(inserted_topics),
        "edges_created": inserted_edges_count,
        "topics": inserted_topics,
    }


async def _extract_from_batch(texts: List[str], subject: str) -> Dict[str, Any]:
    """Extract entities and relations from a batch of text chunks"""
    combined_text = "\n---\n".join(texts)

    # Limit text length to avoid token limits
    if len(combined_text) > 8000:
        combined_text = combined_text[:8000]

    prompt = f"""Bạn là một chuyên gia trích xuất kiến thức từ tài liệu học tập.
Hãy phân tích đoạn văn bản sau và trích xuất đồ thị kiến thức dưới dạng JSON.

YÊU CẦU:
1. Trích xuất TẤT CẢ các khái niệm, định nghĩa, công thức, định lý, ví dụ
2. Xác định mối quan hệ giữa các khái niệm
3. Sử dụng tiếng Việt cho tên khái niệm

Các loại quan hệ được phép:
- prerequisite: A là tiên đề cần học trước B
- sequenceOf: A xếp sau B trong thứ tự học
- relatedTo: A liên quan đến B
- contains: A chứa/chủ đề con B

Định dạng JSON:
{{
  "nodes": [
    {{"name": "tên khái niệm", "type": "concept|definition|formula|theorem|example", "description": "mô tả ngắn", "difficulty": "easy|medium|hard"}}
  ],
  "edges": [
    {{"from_name": "A", "to_name": "B", "relation": "prerequisite|sequenceOf|relatedTo|contains", "weight": 1.0}}
  ]
}}

Nếu không tìm thấy thông tin nào, trả về: {{"nodes": [], "edges": []}}

VĂN BẢN:
{combined_text}

JSON:"""

    llm = get_llm(temperature=0)
    try:
        response = await asyncio.to_thread(llm.invoke, prompt)
        content = response.content
        if isinstance(content, list):
            # Join text parts if it's a list of content blocks
            content = "".join([c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"])
        content = content.strip()
    except Exception:
        logger.exception("LLM batch extraction failed")
        return {"nodes": [], "edges": []}

    # Parse JSON from response
    try:
        # Try to find JSON block
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end]
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end]

        data = json.loads(content.strip())
        return {
            "nodes": data.get("nodes", []),
            "edges": data.get("edges", []),
        }
    except json.JSONDecodeError:
        logger.warning("LLM returned non-JSON content for graph extraction")
        return {"nodes": [], "edges": []}


def _deduplicate_graph(
    entities: List[Dict],
    relations: List[Dict],
) -> tuple[List[Dict], List[Dict]]:
    """Remove duplicate entities and merge duplicate edges"""

    # Deduplicate entities by name (case-insensitive)
    seen_names = {}
    unique_entities = []

    for entity in entities:
        name = entity.get("name", "").strip()
        if not name:
            continue

        name_lower = name.lower()
        if name_lower not in seen_names:
            seen_names[name_lower] = entity
            unique_entities.append(entity)
        else:
            # Merge descriptions
            existing = seen_names[name_lower]
            if not existing.get("description") and entity.get("description"):
                existing["description"] = entity["description"]

    # Deduplicate relations by (from, to, relation) key
    seen_edges = {}
    unique_relations = []

    for edge in relations:
        from_name = (edge.get("from_name") or edge.get("from", "")).strip()
        to_name = (edge.get("to_name") or edge.get("to", "")).strip()
        relation = edge.get("relation", "relatedTo").strip()

        if not from_name or not to_name:
            continue

        key = (from_name.lower(), to_name.lower(), relation.lower())
        if key not in seen_edges:
            seen_edges[key] = edge
            unique_relations.append(edge)
        else:
            # Merge weights
            existing = seen_edges[key]
            existing["weight"] = existing.get("weight", 1.0) + edge.get("weight", 1.0)

    return unique_entities, unique_relations