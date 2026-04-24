import json
import asyncio
from typing import List, Dict, Any
from app.services.neo4j_service import get_neo4j_service
from app.services.document_parser import TextChunk, chunk_for_embedding
from app.utils.gemini_client import get_llm


async def extract_knowledge_graph(
    chunks: List[TextChunk],
    doc_id: str,
    subject: str = "general",
) -> Dict[str, Any]:
    """Main GraphRAG extraction pipeline"""
    neo4j = get_neo4j_service()

    # Phase 1: Batch summarization + entity extraction
    all_entities = []
    all_relations = []

    # Process chunks in batches of 3
    batch_size = 3
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        texts = [c.text for c in batch]

        result = await _extract_from_batch(texts, subject)
        all_entities.extend(result.get("nodes", []))
        all_relations.extend(result.get("edges", []))

    # Phase 2: Deduplication
    entities, relations = _deduplicate_graph(all_entities, all_relations)

    # Phase 3: Insert into Neo4j with many-to-many handling
    inserted_topics = []
    for entity in entities:
        topic_id = neo4j.upsert_topic(
            name=entity["name"],
            description=entity.get("description", ""),
            topic_type=entity.get("type", "concept"),
            difficulty=entity.get("difficulty", "medium"),
            subject=subject,
            doc_id=doc_id,
        )
        inserted_topics.append({
            "name": entity["name"],
            "id": topic_id,
        })

    # Build name -> id mapping
    name_to_id = {t["name"]: t["id"] for t in inserted_topics}

    # Insert edges (only if both endpoints exist)
    inserted_edges = 0
    for edge in relations:
        from_name = edge.get("from_name") or edge.get("from")
        to_name = edge.get("to_name") or edge.get("to")
        if from_name in name_to_id and to_name in name_to_id:
            success = neo4j.upsert_edge(
                from_name=from_name,
                to_name=to_name,
                relation=edge.get("relation", "relatedTo"),
                weight=edge.get("weight", 1.0),
            )
            if success:
                inserted_edges += 1

    return {
        "topics_created": len(inserted_topics),
        "edges_created": inserted_edges,
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
    response = await asyncio.to_thread(llm.invoke, prompt)
    content = response.content.strip()

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