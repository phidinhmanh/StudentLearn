"""Unit tests for assessment engine."""
import pytest
from app.services.assessment_engine import (
    score_to_skill_level,
    normalize_answer,
    compare_answers,
    _get_feedback_message,
)


class TestScoreToSkillLevel:
    """Tests for score_to_skill_level function."""

    def test_zero_correct_returns_level_1(self):
        """0 correct answers should return skill level 1."""
        assert score_to_skill_level(0, 5) == 1
        assert score_to_skill_level(0, 10) == 1

    def test_20_percent_correct_returns_level_1(self):
        """20% or less should return skill level 1."""
        assert score_to_skill_level(1, 5) == 1  # 20%
        assert score_to_skill_level(2, 10) == 1  # 20%

    def test_40_percent_correct_returns_level_2(self):
        """21-60% should return skill level 2."""
        assert score_to_skill_level(2, 5) == 2  # 40%
        assert score_to_skill_level(3, 5) == 2  # 60%

    def test_80_percent_correct_returns_level_3(self):
        """61-100% should return skill level 3."""
        assert score_to_skill_level(4, 5) == 3  # 80%
        assert score_to_skill_level(5, 5) == 3  # 100%
        assert score_to_skill_level(10, 10) == 3  # 100%

    def test_zero_total_returns_level_1(self):
        """Edge case: zero total should not raise error."""
        assert score_to_skill_level(0, 0) == 1

    def test_boundary_21_percent(self):
        """21% should return level 2."""
        assert score_to_skill_level(21, 100) == 2

    def test_boundary_60_percent(self):
        """60% should return level 2."""
        assert score_to_skill_level(60, 100) == 2

    def test_boundary_61_percent(self):
        """61% should return level 3."""
        assert score_to_skill_level(61, 100) == 3


class TestNormalizeAnswer:
    """Tests for normalize_answer function."""

    def test_normalizes_to_uppercase(self):
        """Answer should be converted to uppercase."""
        assert normalize_answer("hello") == "HELLO"
        assert normalize_answer("Hello World") == "HELLO WORLD"

    def test_strips_whitespace(self):
        """Answer should be stripped of leading/trailing whitespace."""
        assert normalize_answer("  hello  ") == "HELLO"
        assert normalize_answer("\t\ntest\n\t") == "TEST"

    def test_empty_string(self):
        """Empty string should return empty string."""
        assert normalize_answer("") == ""
        assert normalize_answer("   ") == ""

    def test_unicode_characters(self):
        """Unicode should be preserved."""
        assert normalize_answer("Hàm số") == "HÀM SỐ"


class TestCompareAnswers:
    """Tests for compare_answers function."""

    def test_multiple_choice_exact_match(self):
        """Multiple choice should require exact match (case-insensitive)."""
        assert compare_answers("A", "A", "multiple_choice") is True
        assert compare_answers("a", "A", "multiple_choice") is True
        assert compare_answers(" B ", "b", "multiple_choice") is True

    def test_multiple_choice_no_match(self):
        """Multiple choice with different answers should not match."""
        assert compare_answers("A", "B", "multiple_choice") is False
        assert compare_answers("C", "A", "multiple_choice") is False

    def test_multiple_choice_empty_answer(self):
        """Empty user answer should not match."""
        assert compare_answers("", "A", "multiple_choice") is False
        assert compare_answers("   ", "A", "multiple_choice") is False

    def test_open_ended_keyword_match(self):
        """Open-ended should match if at least 50% keywords match."""
        correct = "Parabol là đồ thị của hàm số bậc hai"
        user = "Parabol là đồ thị hàm số bậc hai"  # 5/6 words match
        assert compare_answers(user, correct, "open_ended") is True

    def test_open_ended_insufficient_keywords(self):
        """Open-ended with less than 50% match should not match."""
        correct = "Parabol là đồ thị của hàm số bậc hai"
        user = "Parabol"  # 1/6 words match
        assert compare_answers(user, correct, "open_ended") is False

    def test_open_ended_empty_answers(self):
        """Empty answers should not match."""
        assert compare_answers("", "some answer", "open_ended") is False
        assert compare_answers("user answer", "", "open_ended") is False


class TestGetFeedbackMessage:
    """Tests for _get_feedback_message function."""

    def test_skill_level_3_feedback(self):
        """Skill level 3 should have positive feedback."""
        feedback = _get_feedback_message(5, 5, 3)
        assert "Tuyệt vời" in feedback
        assert "100%" in feedback

    def test_skill_level_2_feedback(self):
        """Skill level 2 should have encouraging feedback."""
        feedback = _get_feedback_message(2, 5, 2)
        assert "Khá tốt" in feedback
        assert "40%" in feedback
        assert "ôn tập" in feedback

    def test_skill_level_1_feedback(self):
        """Skill level 1 should have encouraging to study more."""
        feedback = _get_feedback_message(1, 5, 1)
        assert "Cần cố gắng" in feedback
        assert "20%" in feedback
        assert "học lại" in feedback

    def test_zero_total(self):
        """Zero total should not cause division error."""
        feedback = _get_feedback_message(0, 0, 1)
        assert feedback is not None
        assert "0%" in feedback