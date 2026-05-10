package com.knowledgemap.app.ui.components

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.knowledgemap.app.domain.model.DegradationTier
import com.knowledgemap.app.ui.theme.OnBackground
import com.knowledgemap.app.ui.theme.OnSurface
import com.knowledgemap.app.ui.theme.SurfaceBright

@Composable
fun DegradationMemeCard(
    tier: DegradationTier,
    currentD: Double,
    mastery: Double,
    daysSinceLastStudy: Int,
    streakDays: Int,
    modifier: Modifier = Modifier
) {
    EmberCard(
        modifier = modifier,
        borderColor = tier.color
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp),
            verticalAlignment = Alignment.Top
        ) {
            Image(
                painter = painterResource(id = tier.drawableRes),
                contentDescription = tier.description,
                contentScale = ContentScale.Crop,
                modifier = Modifier
                    .width(120.dp)
                    .height(200.dp)
                    .clip(RoundedCornerShape(12.dp))
            )

            Column(
                modifier = Modifier.weight(1f),
                verticalArrangement = Arrangement.spacedBy(10.dp)
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .background(tier.color, RoundedCornerShape(6.dp))
                            .padding(horizontal = 8.dp, vertical = 4.dp)
                    ) {
                        Text(
                            text = tier.label,
                            style = MaterialTheme.typography.labelSmall,
                            color = Color.White,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    Text(
                        text = tier.description,
                        style = MaterialTheme.typography.titleSmall,
                        color = tier.color,
                        fontWeight = FontWeight.SemiBold
                    )
                }

                Text(
                    text = "Chỉ số chuyên cần",
                    style = MaterialTheme.typography.titleSmall,
                    color = OnBackground,
                    fontWeight = FontWeight.SemiBold
                )

                Column(verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(
                            text = "Kiến thức hiện tại",
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurface
                        )
                        Text(
                            text = "${(currentD * 100).toInt()}%",
                            style = MaterialTheme.typography.labelSmall,
                            color = tier.color,
                            fontWeight = FontWeight.Bold
                        )
                    }

                    LinearProgressIndicator(
                        progress = { currentD.toFloat() },
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(6.dp),
                        color = tier.color,
                        trackColor = SurfaceBright,
                        strokeCap = StrokeCap.Round
                    )
                }

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    DegradationStatItem(
                        label = "Mastery",
                        value = "${(mastery * 100).toInt()}%",
                        modifier = Modifier.weight(1f)
                    )
                    DegradationStatItem(
                        label = "Ngày nghỉ",
                        value = daysSinceLastStudy.toString(),
                        modifier = Modifier.weight(1f)
                    )
                    DegradationStatItem(
                        label = "Streak",
                        value = "$streakDays ngày",
                        modifier = Modifier.weight(1f)
                    )
                }
            }
        }
    }
}

@Composable
private fun DegradationStatItem(
    label: String,
    value: String,
    modifier: Modifier = Modifier
) {
    Column(modifier = modifier) {
        Text(
            text = value,
            style = MaterialTheme.typography.titleSmall,
            color = OnBackground,
            fontWeight = FontWeight.SemiBold
        )
        Text(
            text = label,
            style = MaterialTheme.typography.labelSmall,
            color = OnSurface
        )
    }
}