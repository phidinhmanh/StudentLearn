package com.knowledgemap.app.domain.usecase

import org.junit.Assert.*
import org.junit.Test

/**
 * Unit tests for SelfRatingMapper
 * FR-22: Self-rating to Skill Level mapping
 *
 * Mapping:
 * - Hiểu rõ (2) → +1 bậc (không quá 3)
 * - Cần ôn lại (1) → giữ nguyên
 * - Chưa hiểu (0) → -1 bậc (không dưới 0)
 */
class SelfRatingMapperTest {

    private val mapper = SelfRatingMapper()

    // ============== applyRating(int, int) Tests ==============

    @Test
    fun `applyRating Hieu ro from level 0 becomes 1`() {
        val result = mapper.applyRating(0, 2) // Hieu ro
        assertEquals(1, result)
    }

    @Test
    fun `applyRating Hieu ro from level 2 becomes 3`() {
        val result = mapper.applyRating(2, 2) // Hieu ro
        assertEquals(3, result)
    }

    @Test
    fun `applyRating Hieu ro from level 3 stays at 3 (max)`() {
        val result = mapper.applyRating(3, 2) // Hieu ro
        assertEquals(3, result)
    }

    @Test
    fun `applyRating Can on keeps current level`() {
        assertEquals(0, mapper.applyRating(0, 1))
        assertEquals(1, mapper.applyRating(1, 1))
        assertEquals(2, mapper.applyRating(2, 1))
        assertEquals(3, mapper.applyRating(3, 1))
    }

    @Test
    fun `applyRating Chua hieu from level 1 becomes 0`() {
        val result = mapper.applyRating(1, 0) // Chua hieu
        assertEquals(0, result)
    }

    @Test
    fun `applyRating Chua hieu from level 0 stays at 0`() {
        val result = mapper.applyRating(0, 0) // Chua hieu
        assertEquals(0, result)
    }

    @Test
    fun `applyRating invalid rating defaults to CAN_ON`() {
        // Invalid rating 99 should default to CAN_ON (no change)
        assertEquals(2, mapper.applyRating(2, 99))
    }

    // ============== SelfRating enum Tests ==============

    @Test
    fun `SelfRating fromValue 0 returns CHUA_HIEU`() {
        assertEquals(SelfRatingMapper.SelfRating.CHUA_HIEU, SelfRatingMapper.SelfRating.fromValue(0))
    }

    @Test
    fun `SelfRating fromValue 1 returns CAN_ON`() {
        assertEquals(SelfRatingMapper.SelfRating.CAN_ON, SelfRatingMapper.SelfRating.fromValue(1))
    }

    @Test
    fun `SelfRating fromValue 2 returns HIEU_RO`() {
        assertEquals(SelfRatingMapper.SelfRating.HIEU_RO, SelfRatingMapper.SelfRating.fromValue(2))
    }

    @Test
    fun `SelfRating fromValue invalid returns CAN_ON`() {
        assertEquals(SelfRatingMapper.SelfRating.CAN_ON, SelfRatingMapper.SelfRating.fromValue(99))
    }

    // ============== getLabel() Tests ==============

    @Test
    fun `getLabel for rating 0 returns Chua hieu`() {
        assertEquals("Chưa hiểu", mapper.getLabel(0))
    }

    @Test
    fun `getLabel for rating 1 returns Can on lai`() {
        assertEquals("Cần ôn lại", mapper.getLabel(1))
    }

    @Test
    fun `getLabel for rating 2 returns Hieu ro`() {
        assertEquals("Hiểu rõ", mapper.getLabel(2))
    }

    @Test
    fun `getLabel for invalid rating returns Can on lai`() {
        assertEquals("Cần ôn lại", mapper.getLabel(99))
    }

    // ============== getDescription() Tests ==============

    @Test
    fun `getDescription with Hieu ro shows increase message`() {
        val result = mapper.getDescription(1, 2) // Hieu ro from level 1
        assertTrue(result.contains("tăng"))
        assertTrue(result.contains("1"))
        assertTrue(result.contains("2"))
    }

    @Test
    fun `getDescription with Chua hieu shows decrease message`() {
        val result = mapper.getDescription(2, 0) // Chua hieu from level 2
        assertTrue(result.contains("giảm"))
        assertTrue(result.contains("2"))
        assertTrue(result.contains("1"))
    }

    @Test
    fun `getDescription with Can on shows no change message`() {
        val result = mapper.getDescription(2, 1) // Can on from level 2
        assertTrue(result.contains("giữ nguyên"))
    }

    // ============== FR-22 Constraint Tests ==============

    @Test
    fun `FR-22 Hieu ro increases skill level by 1`() {
        // Test all levels 0, 1, 2
        assertEquals(1, mapper.applyRating(0, 2)) // 0+1=1
        assertEquals(2, mapper.applyRating(1, 2)) // 1+1=2
        assertEquals(3, mapper.applyRating(2, 2)) // 2+1=3
    }

    @Test
    fun `FR-22 Hieu ro does not exceed maximum of 3`() {
        assertEquals(3, mapper.applyRating(3, 2)) // 3+1 capped to 3
    }

    @Test
    fun `FR-22 Can on maintains current skill level`() {
        for (level in 0..3) {
            assertEquals(level, mapper.applyRating(level, 1))
        }
    }

    @Test
    fun `FR-22 Chua hieu decreases skill level by 1`() {
        // Test all levels 1, 2, 3
        assertEquals(0, mapper.applyRating(1, 0)) // 1-1=0
        assertEquals(1, mapper.applyRating(2, 0)) // 2-1=1
        assertEquals(2, mapper.applyRating(3, 0)) // 3-1=2
    }

    @Test
    fun `FR-22 Chua hieu does not go below 0`() {
        assertEquals(0, mapper.applyRating(0, 0)) // 0-1 capped to 0
    }
}