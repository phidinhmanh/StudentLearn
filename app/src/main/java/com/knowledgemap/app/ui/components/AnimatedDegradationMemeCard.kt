package com.knowledgemap.app.ui.components

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.Spring
import androidx.compose.animation.core.spring
import androidx.compose.animation.core.tween
import androidx.compose.animation.fadeIn
import androidx.compose.animation.scaleIn
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import com.knowledgemap.app.domain.model.DegradationTier

@Composable
fun AnimatedDegradationMemeCard(
    tier: DegradationTier,
    currentD: Double,
    mastery: Double,
    daysSinceLastStudy: Int,
    streakDays: Int,
    modifier: Modifier = Modifier
) {
    AnimatedVisibility(
        visible = true,
        enter = scaleIn(
            animationSpec = spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = 300f
            ),
            initialScale = 0.8f
        ) + fadeIn(
            animationSpec = tween(durationMillis = 300, delayMillis = 200)
        )
    ) {
        DegradationMemeCard(
            tier = tier,
            currentD = currentD,
            mastery = mastery,
            daysSinceLastStudy = daysSinceLastStudy,
            streakDays = streakDays,
            modifier = modifier
        )
    }
}