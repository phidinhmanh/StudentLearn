package com.knowledgemap.app.domain.model

import androidx.compose.ui.graphics.Color
import com.knowledgemap.app.R
import com.knowledgemap.app.ui.theme.Disabled
import com.knowledgemap.app.ui.theme.Error
import com.knowledgemap.app.ui.theme.Learning
import com.knowledgemap.app.ui.theme.Primary
import com.knowledgemap.app.ui.theme.Secondary

/**
 * Degradation tier based on knowledge decay model:
 *   D = M · e^(-t/S)
 *
 * @param label Short label (e.g. "S Tier")
 * @param description Vietnamese status (e.g. "Rực cháy")
 * @param tierRank Single letter rank (S/A/B/C/D)
 * @param color Compose Color for borders, badges, progress
 * @param drawableRes R.drawable resource ID for the meme image
 */
sealed class DegradationTier(
    val label: String,
    val description: String,
    val tierRank: String,
    val color: Color,
    val drawableRes: Int
) {
    data object STier : DegradationTier(
        label = "S Tier",
        description = "Rực cháy",
        tierRank = "S",
        color = Primary,
        drawableRes = R.drawable.degradation_tier_s_buff_doge
    )

    data object ATier : DegradationTier(
        label = "A Tier",
        description = "Ổn định",
        tierRank = "A",
        color = Secondary,
        drawableRes = R.drawable.degradation_tier_a_bright_campfire
    )

    data object BTier : DegradationTier(
        label = "B Tier",
        description = "Lụi dần",
        tierRank = "B",
        color = Learning,
        drawableRes = R.drawable.degradation_tier_b_dying_embers
    )

    data object CTier : DegradationTier(
        label = "C Tier",
        description = "Nguy cấp",
        tierRank = "C",
        color = Error,
        drawableRes = R.drawable.degradation_tier_c_smoke
    )

    data object DTier : DegradationTier(
        label = "D Tier",
        description = "Tắt ngóm",
        tierRank = "D",
        color = Disabled,
        drawableRes = R.drawable.degradation_tier_d_dark
    )

    companion object {
        /** Map degradation value D to appropriate tier */
        fun fromDegradationValue(d: Double): DegradationTier = when {
            d > 0.8  -> STier
            d > 0.5  -> ATier
            d > 0.2  -> BTier
            d > 0.05 -> CTier
            else     -> DTier
        }
    }
}