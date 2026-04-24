package com.knowledgemap.app.domain.usecase

import org.junit.Assert.*
import org.junit.Test

/**
 * Unit tests for SkillLevelCalculator
 * FR-13: Scoring → Skill Level mapping
 *
 * Test cases:
 * - 0-1 correct → L1 (Cần ôn)
 * - 2-3 correct → L2 (Đang học)
 * - 4-5 correct → L3 (Đã vững)
 */
class SkillLevelCalculatorTest {

    private val calculator = SkillLevelCalculator()

    // ============== calculate() Tests ==============

    @Test
    fun `calculate with 0 correct returns skill level 1`() {
        val result = calculator.calculate(0)
        assertEquals(1, result)
    }

    @Test
    fun `calculate with 1 correct returns skill level 1`() {
        val result = calculator.calculate(1)
        assertEquals(1, result)
    }

    @Test
    fun `calculate with 2 correct returns skill level 2`() {
        val result = calculator.calculate(2)
        assertEquals(2, result)
    }

    @Test
    fun `calculate with 3 correct returns skill level 2`() {
        val result = calculator.calculate(3)
        assertEquals(2, result)
    }

    @Test
    fun `calculate with 4 correct returns skill level 3`() {
        val result = calculator.calculate(4)
        assertEquals(3, result)
    }

    @Test
    fun `calculate with 5 correct returns skill level 3`() {
        val result = calculator.calculate(5)
        assertEquals(3, result)
    }

    @Test
    fun `calculate with negative number returns default skill level 1`() {
        val result = calculator.calculate(-1)
        assertEquals(1, result)
    }

    @Test
    fun `calculate with number greater than 5 returns default skill level 1`() {
        val result = calculator.calculate(10)
        assertEquals(1, result)
    }

    // ============== calculateAfterAssessment() Tests ==============

    @Test
    fun `calculateAfterAssessment with score 0 keeps current level`() {
        // Even with 0 correct, assessment doesn't decrease skill level
        val result = calculator.calculateAfterAssessment(0, 2)
        assertEquals(2, result) // stays at 2
    }

    @Test
    fun `calculateAfterAssessment with score 5 increases to level 3`() {
        val result = calculator.calculateAfterAssessment(5, 1)
        assertEquals(3, result)
    }

    @Test
    fun `calculateAfterAssessment respects maxOf between new and current`() {
        // Even with score of 1, if current is 3, stay at 3
        val result = calculator.calculateAfterAssessment(1, 3)
        assertEquals(3, result)
    }

    @Test
    fun `calculateAfterAssessment with score 3 from level 1 goes to 2`() {
        val result = calculator.calculateAfterAssessment(3, 1)
        assertEquals(2, result)
    }

    // ============== getLabel() Tests ==============

    @Test
    fun `getLabel for level 0 returns Chưa học`() {
        assertEquals("Chưa học", calculator.getLabel(0))
    }

    @Test
    fun `getLabel for level 1 returns Cần ôn`() {
        assertEquals("Cần ôn", calculator.getLabel(1))
    }

    @Test
    fun `getLabel for level 2 returns Đang học`() {
        assertEquals("Đang học", calculator.getLabel(2))
    }

    @Test
    fun `getLabel for level 3 returns Đã vững`() {
        assertEquals("Đã vững", calculator.getLabel(3))
    }

    @Test
    fun `getLabel for invalid level returns Chưa học`() {
        assertEquals("Chưa học", calculator.getLabel(5))
    }

    // ============== getRecommendationReason() Tests ==============

    @Test
    fun `getRecommendationReason with 80 percent returns good result message`() {
        val result = calculator.getRecommendationReason(4, 5)
        assertEquals("Kết quả tốt - củng cố kiến thức", result)
    }

    @Test
    fun `getRecommendationReason with 60 percent returns needs more practice message`() {
        val result = calculator.getRecommendationReason(3, 5)
        assertEquals("Cần ôn tập thêm", result)
    }

    @Test
    fun `getRecommendationReason with 40 percent returns needs restart message`() {
        val result = calculator.getRecommendationReason(2, 5)
        assertEquals("Cần học lại từ đầu", result)
    }

    @Test
    fun `getRecommendationReason with 0 percent returns needs restart message`() {
        val result = calculator.getRecommendationReason(0, 5)
        assertEquals("Cần học lại từ đầu", result)
    }

    @Test
    fun `getRecommendationReason with 100 percent returns good result message`() {
        val result = calculator.getRecommendationReason(5, 5)
        assertEquals("Kết quả tốt - củng cố kiến thức", result)
    }
}