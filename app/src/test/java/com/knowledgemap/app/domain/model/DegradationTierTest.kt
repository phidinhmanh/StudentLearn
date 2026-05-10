package com.knowledgemap.app.domain.model

import org.junit.Assert.assertEquals
import org.junit.Test

class DegradationTierTest {

    @Test
    fun `maps degradation above eighty percent to S tier`() {
        assertEquals(DegradationTier.STier, DegradationTier.fromDegradationValue(0.81))
    }

    @Test
    fun `maps degradation above fifty percent to A tier`() {
        assertEquals(DegradationTier.ATier, DegradationTier.fromDegradationValue(0.51))
    }

    @Test
    fun `maps degradation above twenty percent to B tier`() {
        assertEquals(DegradationTier.BTier, DegradationTier.fromDegradationValue(0.21))
    }

    @Test
    fun `maps degradation above five percent to C tier`() {
        assertEquals(DegradationTier.CTier, DegradationTier.fromDegradationValue(0.06))
    }

    @Test
    fun `maps degradation at five percent to D tier`() {
        assertEquals(DegradationTier.DTier, DegradationTier.fromDegradationValue(0.05))
    }
}