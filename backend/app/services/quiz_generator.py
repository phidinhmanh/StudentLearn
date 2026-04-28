import json
import uuid
import asyncio
import logging
from typing import List, Dict, Any
from app.services.factory import get_graph_service
from app.utils.gemini_client import get_llm

logger = logging.getLogger(__name__)

async def generate_quiz(topic_id: str) -> Dict[str, Any]:
    """Generate quiz for a topic using Unified Schema Mapping."""
    service = get_graph_service()

    # Check for existing quiz
    existing_quiz = await service.get_quiz_by_topic(topic_id)
    if existing_quiz and existing_quiz.get("questions"):
        return {
            "quiz_id": existing_quiz["quiz_id"],
            "topic_id": existing_quiz["topic_id"],
            "questions": _format_questions_for_client(existing_quiz["questions"]),
        }

    # Get topic context from graph
    topic_data = await service.get_topic_with_neighbors(topic_id)
    
    context = ""
    topic_name = topic_id # Default to ID if not found
    
    # Unified Schema Mapping: Try metadata first, then fallback to Semantic Search
    if not topic_data:
        logger.info(f"Entity '{topic_id}' not found in local topics. Falling back to Unified Semantic Search...")
        # Use Semantic Search to find any related Entity/Node
        try:
            search_results = await service.recall(f"Giải thích chi tiết về {topic_id}. Tập trung vào các định nghĩa, công thức và ví dụ liên quan đến kiến thức này.")
            
            if search_results and len(search_results) > 0:
                # recall returns a list of results, we'll join the content/text
                context_texts = []
                for res in search_results:
                    if isinstance(res, dict):
                        # Try to get content or search_result
                        text = res.get("content") or res.get("search_result") or str(res)
                        context_texts.append(text)
                    else:
                        context_texts.append(str(res))
                
                context = "\n---\n".join(context_texts[:3]) # Limit to top 3 for prompt size
                topic_name = topic_id
            else:
                logger.warning(f"No semantic information found for '{topic_id}'.")
                raise ValueError(f"Could not find any information for topic: {topic_id}")
        except Exception as e:
            logger.error(f"Error during semantic search for '{topic_id}': {str(e)}")
            raise
    else:
        topic_name = topic_data['name']
        # Build context prompt from graph data
        context_parts = []
        context_parts.append(f"Khái niệm: {topic_data['name']}")
        if topic_data.get("description"):
            context_parts.append(f"Mô tả: {topic_data['description']}")

        # Add prerequisite context (Unified edges)
        prereqs = topic_data.get("prereqs_from", [])
        if prereqs:
            prereq_names = [p["node"]["name"] for p in prereqs if p.get("node")]
            context_parts.append(f"Kiến thức nền tảng: {', '.join(prereq_names)}")

        # Add related topics
        related = topic_data.get("related", [])
        if related:
            related_names = [r["node"]["name"] for r in related if r.get("node")]
            context_parts.append(f"Chủ đề liên quan: {', '.join(related_names)}")

        context = "\n".join(context_parts)

    # Generate quiz via Gemini
    prompt = f"""Bạn là giáo viên Toán THPT. Tạo 5 câu hỏi trắc nghiệm để kiểm tra hiểu bài cho chủ đề sau:

CHỦ ĐỀ:
{context}

YÊU CẦU:
- 2 câu hỏi kiến thức cơ bản (recall): định nghĩa, công thức
- 2 câu hỏi áp dụng: giải bài toán, tính toán
- 1 câu hỏi giải thích: chứng minh, suy luận

Mỗi câu hỏi có:
- id: chuỗi duy nhất
- text: nội dung câu hỏi
- type: "multiple_choice" hoặc "open_ended"
- options: mảng 4 lựa chọn cho MCQ, rỗng cho open-ended
- correct_answer: đáp án đúng (A/B/C/D cho MCQ, text cho open-ended)
- explanation: giải thích ngắn tại sao đúng

Định dạng JSON:
{{
  "questions": [
    {{
      "id": "q1",
      "text": "Câu hỏi ở đây?",
      "type": "multiple_choice",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "A",
      "explanation": "Giải thích..."
    }}
  ]
}}

QUAN TRỌNG: Chỉ trả về JSON, không có giải thích gì thêm."""

    llm = get_llm(temperature=0.5)
    try:
        response = await asyncio.to_thread(llm.invoke, prompt)
        content = response.content.strip()
    except Exception:
        questions = _generate_fallback_questions(topic_name)
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

            data = json.loads(content.strip())
            questions = data.get("questions", [])
        except json.JSONDecodeError:
            # Fallback to simple 5 questions
            questions = _generate_fallback_questions(topic_name)

    # Save quiz to Graph
    quiz_id = str(uuid.uuid4())
    await service.save_quiz(quiz_id, topic_id, questions)

    return {
        "quiz_id": quiz_id,
        "topic_id": topic_id,
        "questions": _format_questions_for_client(questions),
    }


def _format_questions_for_client(questions: List[Dict]) -> List[Dict]:
    """Remove correct_answer before sending to client"""
    return [
        {
            "id": q.get("id", str(uuid.uuid4())),
            "text": q.get("text", ""),
            "type": q.get("type", "multiple_choice"),
            "options": q.get("options", []),
            "explanation": q.get("explanation", ""),
        }
        for q in questions
    ]


def _generate_fallback_questions(topic_name: str) -> List[Dict]:
    """Fallback questions if Gemini parsing fails"""
    return [
        {
            "id": "f1",
            "text": f"{topic_name} là gì?",
            "type": "multiple_choice",
            "options": [
                "A. Một khái niệm cơ bản",
                "B. Một định lý quan trọng",
                "C. Một công thức",
                "D. Một phương pháp giải",
            ],
            "correct_answer": "A",
            "explanation": f"{topic_name} là một khái niệm cơ bản trong chương trình.",
        },
        {
            "id": "f2",
            "text": f"Nêu đặc điểm chính của {topic_name}?",
            "type": "open_ended",
            "options": [],
            "correct_answer": "",
            "explanation": "Cần nắm vững đặc điểm cơ bản.",
        },
        {
            "id": "f3",
            "text": f"Ứng dụng của {topic_name} trong thực tế?",
            "type": "multiple_choice",
            "options": [
                "A. Ứng dụng 1",
                "B. Ứng dụng 2",
                "C. Ứng dụng 3",
                "D. Tất cả các đáp án trên",
            ],
            "correct_answer": "D",
            "explanation": "Có nhiều ứng dụng quan trọng.",
        },
        {
            "id": "f4",
            "text": f"Công thức liên quan đến {topic_name}?",
            "type": "open_ended",
            "options": [],
            "correct_answer": "",
            "explanation": "Cần nhớ công thức cơ bản.",
        },
        {
            "id": "f5",
            "text": f"So sánh {topic_name} với các khái niệm đã học?",
            "type": "open_ended",
            "options": [],
            "correct_answer": "",
            "explanation": "Liên hệ với kiến thức cũ.",
        },
    ]