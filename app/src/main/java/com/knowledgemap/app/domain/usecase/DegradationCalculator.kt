package com.knowledgemap.app.domain.usecase

import javax.inject.Inject
import javax.inject.Singleton
import kotlin.math.exp
import kotlin.math.ln

/**
 * Knowledge degradation calculator using the Forgetting Curve model.
 *
 *   D = M · e^(-t/S)
 *
 * - D: current knowledge level (0.0 – 1.0)
 * - M: maximum mastery at last study session (0.0 – 1.0)
 * - t: days elapsed since last study
 * - S: strength / half-life constant in days (default 7 = 1 week half-life)
 */
@Singleton
class DegradationCalculator @Inject constructor() {

    companion object {
        const val DEFAULT_STRENGTH = 7.0
    }

    /**
     * Calculate current knowledge level D.
     *
     * @param mastery Max mastery at last study (0.0 – 1.0)
     * @param daysSinceLastStudy Days since last study session
     * @param strength Strength/half-life constant (default 7 days)
     * @return Degradation value D clamped to [0.0, 1.0]
     */
    fun calculate(
        mastery: Double,
        daysSinceLastStudy: Int,
        strength: Double = DEFAULT_STRENGTH
    ): Double {
        require(mastery in 0.0..1.0) { "mastery must be in [0, 1]" }
        require(strength > 0) { "strength constant must be positive" }
        require(daysSinceLastStudy >= 0) { "daysSinceLastStudy must be non-negative" }

        val d = mastery * exp(-daysSinceLastStudy / strength)
        return d.coerceIn(0.0, 1.0)
    }

    /**
     * Calculate days until knowledge degrades below threshold.
     * Rearranged: t = -S · ln(D_target / M)
     *
     * @param mastery Max mastery at last study
     * @param threshold Target knowledge level
     * @param strength Strength/half-life constant
     * @return Days until threshold, or null if already below
     */
    fun daysUntilThreshold(
        mastery: Double,
        threshold: Double,
        strength: Double = DEFAULT_STRENGTH
    ): Int? {
        require(mastery in 0.0..1.0) { "mastery must be in [0, 1]" }
        require(threshold in 0.0..1.0) { "threshold must be in [0, 1]" }
        require(threshold > 0) { "threshold must be positive" }
        if (mastery <= threshold) return null

        val days = -strength * ln(threshold / mastery)
        return days.toInt().coerceAtLeast(0)
    }
}