import json
import asyncio
from typing import Dict, Any, List
from app.services.factory import get_graph_service
from app.utils.gemini_client import get_llm


async def get_personalized_path(
    user_id: str,
    goal: str = "master_all",
) -> Dict[str, Any]:
    """Get personalized learning path for user, using cache if available"""
    service = get_graph_service()

    # Try cached path first
    cached = await service.get_learning_path(user_id)
    if cached and cached.get("path_json"):
        return json.loads(cached["path_json"])

    # Generate new path
    return await generate_learning_path(user_id, goal)


async def generate_learning_path(
    user_id: str,
    goal: str = "master_all",
) -> Dict[str, Any]:
    """Generate personalized learning path using Gemini"""
    service = get_graph_service()

    # Get all topics
    all_topics = await service.get_all_topics()
    if not all_topics:
        return {"path": [], "message": "Chưa có chủ đề nào trong hệ thống"}

    # Get user progress
    progress = await service.get_user_progress(user_id)
    progress_map = {p["topic_id"]: p["skill_level"] for p in progress}

    # Categorize topics
    mastered = []
    learning = []
    locked = []
    not_started = []

    for topic in all_topics:
        tid = topic["id"]
        skill_level = progress_map.get(tid, 0)

        if skill_level >= 3:
            mastered.append(topic)
        elif skill_level >= 2:
            learning.append(topic)
        elif skill_level == 1:
            learning.append(topic)
        else:
            # Check if prerequisites are met
            prereqs = topic.get("prerequisites", [])
            if prereqs:
                # Simplified: check if at least one prereq is at level 2+
                prereqs_met = any(
                    progress_map.get(p.get("id", ""), 0) >= 2
                    for p in prereqs
                    if isinstance(p, dict)
                )
                if prereqs_met:
                    not_started.append(topic)
                else:
                    locked.append(topic)
            else:
                not_started.append(topic)

    # Build context for Gemini
    context = f"""Số lượng chủ đề: {len(all_topics)}

Chủ đề đã thành thạo ({len(mastered)}): {', '.join([t['name'] for t in mastered[:10]])}
Chủ đề đang học ({len(learning)}): {', '.join([t['name'] for t in learning[:10]])}
Chủ đề chưa bắt đầu ({len(not_started)}): {', '.join([t['name'] for t in not_started[:15]])}
Chủ đề bị khóa ({len(locked)}): {', '.join([t['name'] for t in locked[:5]])}

Chi tiết từng chủ đề chưa bắt đầu và đang học:
{_format_topics_detail(not_started + learning)}

MỤC TIÊU NGƯỜI DÙNG: {goal}"""

    prompt = f"""Bạn là chuyên gia tư vấn lộ trình học tập. Phân tích tình trạng học tập và tạo lộ trình cá nhân hóa.

THÔNG TIN HIỆN TẠI:
{context}

YÊU CẦU LỘ TRÌNH:
1. Ưu tiên: Chủ đề sẵn sàng học (prerequisites đã đủ)
2. Tiếp theo: Lấp đầy lỗ hổng prerequisite
3. Cuối cùng: Ôn tập chủ đề cần củng cố

Mỗi chủ đề trong lộ trình cần có:
- topic_id: ID của chủ đề
- name: tên chủ đề
- priority: thứ tự ưu tiên (1, 2, 3...)
- reason: lý do đưa vào lộ trình
- estimated_time: ước tính thời gian (vd: "30 phút", "1 giờ")
- status: "ready" | "review" | "locked"

Trả về JSON:
{{
  "path": [
    {{"topic_id": "...", "name": "...", "priority": 1, "reason": "Sẵn sàng học vì đã nắm vững prerequisite", "estimated_time": "30 phút", "status": "ready"}}
  ],
  "summary": "Tổng quan ngắn gọn về lộ trình"
}}

QUAN TRỌNG: Chỉ trả về JSON, không có giải thích gì thêm."""

    llm = get_llm(temperature=0.3)
    try:
        response = await llm.ainvoke(prompt)
        content = response.content.strip()
    except Exception:
        path_data = _generate_simple_path(all_topics, progress_map)
    else:
        # Parse JSON
        try:
            if "```json" in content:
                start = content.find("```json") + 7
                end = content.find("```", start)
                content = content[start:end]
            elif "```" in content:
                start = content.find("```") + 3
                end = content.find("```", start)
                content = content[start:end]

            path_data = json.loads(content.strip())
        except json.JSONDecodeError:
            # Fallback: simple path based on graph structure
            path_data = _generate_simple_path(all_topics, progress_map)

    # Cache the path
    await service.save_learning_path(user_id, json.dumps(path_data, ensure_ascii=False))

    return path_data


def _format_topics_detail(topics: List[Dict]) -> str:
    """Format topics for Gemini prompt"""
    lines = []
    for t in topics[:20]:  # Limit to avoid token overflow
        lines.append(f"- {t['name']}: {t.get('description', 'Không có mô tả')}")
    return "\n".join(lines)


def _generate_simple_path(topics: List[Dict], progress_map: Dict[str, int]) -> Dict[str, Any]:
    """Fallback simple path generation"""
    path = []
    priority = 1

    # Sort by name for consistency
    for topic in sorted(topics, key=lambda t: t.get("name", "")):
        tid = topic["id"]
        skill_level = progress_map.get(tid, 0)

        if skill_level < 3:
            status = "ready" if skill_level > 0 else "ready"
            reason = "Đã sẵn sàng để học"

            if skill_level == 0:
                reason = "Chủ đề mới, có thể bắt đầu"
            elif skill_level == 1:
                reason = "Cần ôn tập và nâng cao"

            path.append({
                "topic_id": tid,
                "name": topic["name"],
                "priority": priority,
                "reason": reason,
                "estimated_time": "30 phút",
                "status": status,
            })
            priority += 1

    return {
        "path": path[:10],  # Limit to 10
        "summary": f"Lộ trình gồm {len(path[:10])} chủ đề ưu tiên",
    }