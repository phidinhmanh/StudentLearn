from typing import List, Dict, Any
from app.services.neo4j_service import get_neo4j_service


def score_to_skill_level(correct_count: int, total: int) -> int:
    """Map correct count to skill level (1-3)"""
    percentage = correct_count / total if total > 0 else 0
    if percentage <= 0.2:
        return 1  # L1: needs review
    elif percentage <= 0.6:
        return 2  # L2: partial understanding
    else:
        return 3  # L3: mastered


def normalize_answer(answer: str) -> str:
    """Normalize answer for comparison"""
    if not answer:
        return ""
    return answer.strip().upper()


def compare_answers(user_answer: str, correct_answer: str, question_type: str) -> bool:
    """Compare user answer with correct answer"""
    user_norm = normalize_answer(user_answer)
    correct_norm = normalize_answer(correct_answer)

    if not user_norm or not correct_norm:
        return False

    if question_type == "multiple_choice":
        # Direct match for A/B/C/D
        return user_norm == correct_norm
    else:
        # For open-ended, check if key answer words are present
        correct_words = set(correct_norm.lower().split())
        user_words = set(user_norm.lower().split())
        overlap = len(correct_words & user_words)
        return overlap >= len(correct_words) * 0.5 if correct_words else False


async def evaluate_quiz(
    user_id: str,
    quiz_id: str,
    answers: List[Dict[str, str]],
) -> Dict[str, Any]:
    """Evaluate quiz answers and update user progress"""
    neo4j = get_neo4j_service()

    # Get full quiz with correct answers
    quiz = neo4j.get_quiz(quiz_id)
    if not quiz:
        raise ValueError(f"Quiz not found: {quiz_id}")

    questions = quiz.get("questions", [])
    if not questions:
        raise ValueError("Quiz has no questions")

    # Build answer map
    answer_map = {a["question_id"]: a["answer"] for a in answers}

    # Score each question
    results = []
    correct_count = 0

    for q in questions:
        q_id = q.get("id", "")
        user_answer = answer_map.get(q_id, "")
        correct_answer = q.get("correct_answer", "")
        q_type = q.get("type", "multiple_choice")

        is_correct = compare_answers(user_answer, correct_answer, q_type)
        if is_correct:
            correct_count += 1

        results.append({
            "question_id": q_id,
            "question_text": q.get("text", ""),
            "user_answer": user_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })

    total = len(questions)
    skill_level = score_to_skill_level(correct_count, total)

    # Update progress
    topic_id = quiz["topic_id"]
    neo4j.upsert_progress(user_id, topic_id, skill_level)

    # Invalidate learning path (needs regeneration)
    neo4j.invalidate_learning_path(user_id)

    # Get feedback message
    feedback = _get_feedback_message(correct_count, total, skill_level)

    return {
        "quiz_id": quiz_id,
        "topic_id": topic_id,
        "correct_count": correct_count,
        "total": total,
        "score": f"{correct_count}/{total}",
        "skill_level": skill_level,
        "feedback": feedback,
        "results": results,
    }


def _get_feedback_message(correct_count: int, total: int, skill_level: int) -> str:
    """Generate feedback message based on score"""
    percentage = (correct_count / total * 100) if total > 0 else 0

    if skill_level == 3:
        return f"Tuyệt vời! Bạn đã hiểu rõ chủ đề này ({int(percentage)}% đúng). Hãy tiếp tục với các chủ đề tiếp theo!"
    elif skill_level == 2:
        return f"Khá tốt! Bạn hiểu được {int(percentage)}% nội dung. Cần ôn tập thêm một số phần để đạt mức thành thạo."
    else:
        return f"Cần cố gắng hơn! Bạn chỉ đúng {int(percentage)}%. Hãy học lại lý thuyết và làm lại bài tập."