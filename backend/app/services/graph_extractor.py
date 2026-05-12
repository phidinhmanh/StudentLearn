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
    """Main GraphRAG extraction pipeline — Using direct LLM for speed and stability"""
    service = get_graph_service()

    # Cognee automatic ingestion is disabled here to avoid stability issues (TypeError/Timeouts)
    # We use manual LLM extraction below which is much faster.

    # Regroup chunks into larger context windows (e.g. 15000 chars) to reduce LLM calls
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

    # Phase 3: Semantic Aggregation — merge repetitive near-duplicate topics into master topics
    if len(entities) > 1:
        entities, relations = await _aggregate_semantic_topics(entities, relations, subject)

    # Phase 4: Insert into service using batch methods.
    # ``service`` implements asynchronous methods in the real CogneeService,
    # but our test suite uses a simple MagicMock that provides *synchronous*
    # callables. To support both, we inspect whether the attribute is a coroutine
    # function and ``await`` only when appropriate.
    if hasattr(service, "batch_upsert_topics"):
        if asyncio.iscoroutinefunction(service.batch_upsert_topics):
            inserted_topics = await service.batch_upsert_topics(entities, doc_id)
        else:
            inserted_topics = service.batch_upsert_topics(entities, doc_id)
    else:
        inserted_topics = []

    # Insert edges in batch – same async/sync handling as above.
    inserted_edges_count = 0
    if hasattr(service, "batch_upsert_edges"):
        if asyncio.iscoroutinefunction(service.batch_upsert_edges):
            inserted_edges_count = await service.batch_upsert_edges(relations)
        else:
            inserted_edges_count = service.batch_upsert_edges(relations)

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


async def _aggregate_semantic_topics(
    entities: List[Dict],
    relations: List[Dict],
    subject: str,
) -> tuple[List[Dict], List[Dict]]:
    """Use LLM-based entity resolution to merge repetitive educational topics into cleaner master topics."""
    if len(entities) <= 1:
        return entities, relations

    entity_payload = [
        {
            "name": e.get("name", ""),
            "type": e.get("type", "concept"),
            "description": e.get("description", ""),
            "difficulty": e.get("difficulty", "medium"),
        }
        for e in entities[:120]
    ]
    relation_payload = [
        {
            "from_name": r.get("from_name") or r.get("from", ""),
            "to_name": r.get("to_name") or r.get("to", ""),
            "relation": r.get("relation", "relatedTo"),
            "weight": r.get("weight", 1.0),
        }
        for r in relations[:200]
    ]

    prompt = f"""Bạn là chuyên gia chuẩn hóa kiến thức THPT Việt Nam.
Nhiệm vụ: thực hiện entity resolution để gộp các topic trùng lặp/ngữ nghĩa gần nhau thành MASTER TOPIC chất lượng cao.

MỤC TIÊU:
- Gộp các mục trùng ngữ nghĩa như Venn/Venn-Euler/Biểu đồ Ven/Biểu đồ Venn thành 1 topic sạch.
- Giữ cấu trúc phân cấp rõ ràng.
- Chuẩn hóa thuật ngữ theo chương trình THPT.
- Không bám sát từng từ trong PDF nếu từ đó làm graph bị rác hoặc lặp.

QUY TẮC:
- Chỉ gộp khi thật sự cùng một ý nghĩa cốt lõi.
- Ưu tiên tên master topic rõ, chuyên nghiệp, dùng tiếng Việt.
- Ví dụ tốt: 'Phương pháp trực quan hóa với Biểu đồ Venn & Euler'.
- Không tạo quá nhiều topic vi mô nếu chúng chỉ là biến thể diễn đạt.

INPUT NODES:
{json.dumps(entity_payload, ensure_ascii=False)}

INPUT EDGES:
{json.dumps(relation_payload, ensure_ascii=False)}

Hãy trả về JSON có dạng:
{{
  "nodes": [{{"name":"...","type":"concept|definition|formula|theorem|example","description":"...","difficulty":"easy|medium|hard"}}],
  "edges": [{{"from_name":"...","to_name":"...","relation":"prerequisite|sequenceOf|relatedTo|contains","weight":1.0}}]
}}

Chỉ trả về JSON."""

    llm = get_llm(temperature=0)
    try:
        response = await asyncio.to_thread(llm.invoke, prompt)
        content = response.content
        if isinstance(content, list):
            content = "".join([c.get("text", "") for c in content if isinstance(c, dict) and c.get("type") == "text"])
        content = content.strip()
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end]
        elif "```" in content:
            start = content.find("```") + 3
            end = content.find("```", start)
            content = content[start:end]
        data = json.loads(content.strip())
        merged_nodes = data.get("nodes", []) or entities
        merged_edges = data.get("edges", []) or relations
        return _deduplicate_graph(merged_nodes, merged_edges)
    except Exception:
        logger.exception("Semantic topic aggregation failed; using deduplicated graph")
        return entities, relations


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