package com.knowledgemap.app.domain.usecase

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class DegradationCalculatorTest {

    private val calculator = DegradationCalculator()

    @Test
    fun `calculate with zero elapsed days returns mastery unchanged`() {
        val result = calculator.calculate(mastery = 0.72, daysSinceLastStudy = 0)

        assertEquals(0.72, result, 0.0001)
    }

    @Test
    fun `calculate with one elapsed day returns A tier range`() {
        val result = calculator.calculate(mastery = 0.72, daysSinceLastStudy = 1, strength = 7.0)

        assertEquals(0.6247, result, 0.001)
        assertTrue(result > 0.5 && result <= 0.8)
    }

    @Test
    fun `calculate with seven elapsed days from perfect mastery returns B tier range`() {
        val result = calculator.calculate(mastery = 1.0, daysSinceLastStudy = 7, strength = 7.0)

        assertEquals(0.3678, result, 0.001)
        assertTrue(result > 0.2 && result <= 0.5)
    }

    @Test
    fun `calculate with zero mastery returns zero`() {
        val result = calculator.calculate(mastery = 0.0, daysSinceLastStudy = 5)

        assertEquals(0.0, result, 0.0)
    }

    @Test(expected = IllegalArgumentException::class)
    fun `calculate rejects mastery greater than one`() {
        calculator.calculate(mastery = 1.5, daysSinceLastStudy = 1)
    }

    @Test(expected = IllegalArgumentException::class)
    fun `calculate rejects negative days`() {
        calculator.calculate(mastery = 0.5, daysSinceLastStudy = -1)
    }

    @Test(expected = IllegalArgumentException::class)
    fun `calculate rejects non-positive strength`() {
        calculator.calculate(mastery = 0.5, daysSinceLastStudy = 1, strength = 0.0)
    }

    @Test
    fun `daysUntilThreshold returns null when mastery already below threshold`() {
        val result = calculator.daysUntilThreshold(mastery = 0.5, threshold = 0.6)

        assertNull(result)
    }

    @Test
    fun `daysUntilThreshold returns seven days for e inverse threshold`() {
        val result = calculator.daysUntilThreshold(mastery = 1.0, threshold = 0.3678, strength = 7.0)

        assertEquals(7, result)
    }
}