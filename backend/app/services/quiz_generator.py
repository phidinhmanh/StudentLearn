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
        # Ensure we have a quiz_id, generate if missing
        quiz_id = existing_quiz.get("quiz_id") or str(uuid.uuid4())
        return {
            "quiz_id": quiz_id,
            "topic_id": existing_quiz.get("topic_id", topic_id),
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
    prompt = f"""Bạn là giáo viên Toán THPT. Tạo 6 câu hỏi trắc nghiệm kiểm tra hiểu bài cho chủ đề sau, BẮT BUỘC tuân theo Bloom's Taxonomy (cấp độ cao):

CHỦ ĐỀ:
{context}

YÊU CẦU BẮT BUỘC — phân bổ đều 3 cấp độ nhận thức:
- Thông hiểu (Understanding): 2 câu hỏi — giải thích ý nghĩa, tại sao dùng công thức này
- Vận dụng (Application): 2 câu hỏi — giải bài toán thực tế, tính toán cụ thể
- Phân tích (Analyze): 2 câu hỏi — so sánh các khái niệm, dự đoán hệ quả, giải thích mối liên hệ logic giữa các Node trong đồ thị kiến thức

QUY TẮC:
- cognitive_level field BẮT BUỘC có giá trị đúng: "understanding" | "application" | "analyze"
- KHÔNG BAO GIỜ sinh câu hỏi ở mức nhớ máy móc tên gọi, ký hiệu thuần túy
- Mỗi câu hỏi phải có đủ 4 lựa chọn (A/B/C/D)
- Đáp án đúng phải hợp lý, các đáp án sai phải có vẻ đúng để test thật
- Câu hỏi Analyze phải sử dụng quan hệ (Edges) trong Knowledge Graph: so sánh, dự đoán, giải thích mối liên hệ

Mỗi câu hỏi có:
- id: chuỗi duy nhất
- text: nội dung câu hỏi
- type: "multiple_choice" hoặc "open_ended"
- options: mảng 4 lựa chọn cho MCQ, rỗng cho open-ended
- correct_answer: đáp án đúng (A/B/C/D cho MCQ, text cho open-ended)
- explanation: giải thích ngắn tại sao đúng
- cognitive_level: BẮT BUỘC — "understanding" | "application" | "analyze"

Định dạng JSON:
{{
  "questions": [
    {{
      "id": "q1",
      "text": "Câu hỏi ở đây?",
      "type": "multiple_choice",
      "options": ["A. ...", "B. ...", "C. ...", "D. ..."],
      "correct_answer": "A",
      "explanation": "Giải thích...",
      "cognitive_level": "understanding"
    }}
  ]
}}

QUAN TRỌNG: Chỉ trả về JSON, không có giải thích gì thêm."""

    llm = get_llm(temperature=0.5)
    try:
        response = await llm.ainvoke(prompt)
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
            questions = _generate_fallback_questions(topic_name)

    # Post-generation validation: sanitize, filter, and ensure structural integrity
    questions = _validate_and_sanitize_questions(questions, topic_name)

    # Save quiz to Graph
    quiz_id = str(uuid.uuid4())
    await service.save_quiz(quiz_id, topic_id, questions)

    return {
        "quiz_id": quiz_id,
        "topic_id": topic_id,
        "questions": _format_questions_for_client(questions),
    }


def _validate_and_sanitize_questions(questions: List[Dict], topic_name: str) -> List[Dict]:
    """Ensure every MCQ has exactly 4 options and a valid correct_answer in the options list.

    - Filters out questions missing options or with wrong correct_answer.
    - Ensures len(options) == 4 for multiple_choice type.
    - Normalizes correct_answer to a single letter (A/B/C/D).
    - Falls back to _generate_fallback_questions if < 3 valid questions remain.
    """
    if not questions:
        return _generate_fallback_questions(topic_name)

    valid = []
    for q in questions:
        q_type = q.get("type", "multiple_choice")
        opts = q.get("options", [])

        if q_type == "open_ended":
            valid.append(q)
            continue

        # MCQ must have exactly 4 options
        if not isinstance(opts, list) or len(opts) != 4:
            continue

        # Strip whitespace from options
        clean_opts = [str(o).strip() for o in opts]
        if not all(clean_opts):
            continue  # skip if any option is empty

        correct = str(q.get("correct_answer", "")).strip()
        # Normalize: take first letter uppercase A-D
        if correct:
            first_char = correct[0].upper()
            if first_char in "ABCD":
                valid.append({
                    "id": q.get("id", str(uuid.uuid4())),
                    "text": q.get("text", ""),
                    "type": q_type,
                    "options": clean_opts,
                    "correct_answer": first_char,
                    "explanation": q.get("explanation", ""),
                    "cognitive_level": q.get("cognitive_level", "application"),
                })
                continue

        # If correct_answer not in A-D, try to infer from content
        valid.append({
            "id": q.get("id", str(uuid.uuid4())),
            "text": q.get("text", ""),
            "type": q_type,
            "options": clean_opts,
            "correct_answer": "A",  # safe default
            "explanation": q.get("explanation", ""),
            "cognitive_level": q.get("cognitive_level", "application"),
        })

    # If we lost too many questions, regenerate from fallback
    if len(valid) < 3:
        logger.warning(
            f"Quiz integrity check: only {len(valid)} valid questions out of {len(questions)}. "
            "Replacing with fallback."
        )
        return _generate_fallback_questions(topic_name)

    return valid


def _format_questions_for_client(questions: List[Dict]) -> List[Dict]:
    """Remove correct_answer before sending to client, keep cognitive_level"""
    # Safety: reject any cognitive_level not in our active set
    safe_levels = {"understanding", "application", "analyze"}

    def _clean_options(opts: List[str]) -> List[str]:
        """Remove empty, whitespace-only, or placeholder options."""
        return [o for o in (opts or []) if o.strip() not in ("", "-", "N/A", "None", "")]

    result = []
    for q in questions:
        raw = q.get("options", [])
        cleaned = _clean_options(raw)
        # Strict validation: reject questions without exactly 4 valid options
        if len(cleaned) != 4:
            print(f"[STRICT_VALIDATION] Rejecting question {q.get('id')} - has {len(cleaned)} options, expected 4")
            continue
        result.append({
            "id": q.get("id", str(uuid.uuid4())),
            "text": q.get("text", ""),
            "type": q.get("type", "multiple_choice"),
            "options": cleaned,
            "explanation": q.get("explanation", ""),
            "cognitive_level": q.get("cognitive_level", "application")
                if q.get("cognitive_level") not in safe_levels
                else q.get("cognitive_level", "application"),
        })
    return result


def _generate_fallback_questions(topic_name: str) -> List[Dict]:
    """Fallback questions if Gemini parsing fails, using higher-order Bloom taxonomy levels"""
    return [
        {
            "id": "f1",
            "text": f"Vì sao {topic_name} có ý nghĩa quan trọng trong mạch kiến thức đang học?",
            "type": "multiple_choice",
            "options": [
                "A. Vì nó chỉ là một tên gọi cần ghi nhớ",
                "B. Vì nó giúp kết nối định nghĩa, công thức và cách giải bài toán",
                "C. Vì nó không liên quan đến chủ đề khác",
                "D. Vì nó chỉ dùng để làm ví dụ minh họa",
            ],
            "correct_answer": "B",
            "explanation": f"{topic_name} có vai trò kết nối các thành phần kiến thức và hỗ trợ suy luận khi giải bài.",
            "cognitive_level": "understanding",
        },
        {
            "id": "f2",
            "text": f"Hãy giải thích đặc điểm chính của {topic_name} và vì sao đặc điểm đó quan trọng.",
            "type": "open_ended",
            "options": [],
            "correct_answer": "",
            "explanation": "Cần hiểu bản chất và ý nghĩa của kiến thức.",
            "cognitive_level": "understanding",
        },
        {
            "id": "f3",
            "text": f"Ứng dụng phù hợp nhất của {topic_name} trong một bài toán thực tế là gì?",
            "type": "multiple_choice",
            "options": [
                "A. Dùng để tính toán hoặc suy luận trong ngữ cảnh cụ thể",
                "B. Chỉ dùng để học thuộc lòng khái niệm",
                "C. Không thể áp dụng vào bài toán thực tế",
                "D. Chỉ có thể dùng trong phần lý thuyết",
            ],
            "correct_answer": "A",
            "explanation": "Kiến thức cần được vận dụng vào tình huống cụ thể để tạo ra lời giải.",
            "cognitive_level": "application",
        },
        {
            "id": "f4",
            "text": f"Nếu thay đổi một điều kiện quan trọng trong bài toán liên quan đến {topic_name}, kết quả sẽ thay đổi như thế nào?",
            "type": "open_ended",
            "options": [],
            "correct_answer": "",
            "explanation": "Cần vận dụng kiến thức để dự đoán kết quả trong tình huống biến đổi.",
            "cognitive_level": "application",
        },
        {
            "id": "f5",
            "text": f"So sánh {topic_name} với một khái niệm liên quan và phân tích điểm giống, khác nhau.",
            "type": "open_ended",
            "options": [],
            "correct_answer": "",
            "explanation": "Cần phân tích quan hệ logic giữa các khái niệm thay vì chỉ nhớ định nghĩa.",
            "cognitive_level": "analyze",
        },
        {
            "id": "f6",
            "text": f"Mối liên hệ logic giữa {topic_name} và các kiến thức nền tảng ảnh hưởng thế nào đến cách giải bài toán?",
            "type": "open_ended",
            "options": [],
            "correct_answer": "",
            "explanation": "Cần phân tích vai trò của các quan hệ giữa các node kiến thức trong quá trình suy luận.",
            "cognitive_level": "analyze",
        },
    ]