package com.knowledgemap.app.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.composed
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.knowledgemap.app.R
import com.knowledgemap.app.domain.model.TopicNode
import com.knowledgemap.app.domain.model.TopicStatus
import com.knowledgemap.app.ui.theme.*

fun Modifier.shimmerEffect(): Modifier = composed {
    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateAnim = transition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer_translate"
    )

    val shimmerColors = listOf(
        Color.LightGray.copy(alpha = 0.6f),
        Color.LightGray.copy(alpha = 0.2f),
        Color.LightGray.copy(alpha = 0.6f),
    )

    val brush = Brush.linearGradient(
        colors = shimmerColors,
        start = Offset.Zero,
        end = Offset(x = translateAnim.value, y = translateAnim.value)
    )
    background(brush)
}

@Composable
fun hapticClick(): () -> Unit {
    val haptic = LocalHapticFeedback.current
    return {
        haptic.performHapticFeedback(HapticFeedbackType.LongPress)
    }
}


@Composable
fun EmberCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    borderColor: Color = Outline,
    content: @Composable () -> Unit
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .then(if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier)
            .border(1.dp, borderColor, MaterialTheme.shapes.large),
        shape = MaterialTheme.shapes.large,
        colors = CardDefaults.cardColors(
            containerColor = Surface
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Column(
            modifier = Modifier.padding(16.dp)
        ) {
            content()
        }
    }
}

@Composable
fun EmberListItem(
    topic: TopicNode,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val status = topic.status
    val skillColor = getSkillLevelColor(topic.skillLevel)
    val isLocked = status == TopicStatus.LOCKED

    EmberCard(
        modifier = modifier,
        onClick = if (!isLocked) onClick else null,
        borderColor = if (status == TopicStatus.LEARNING) Tertiary else Outline
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Box(contentAlignment = Alignment.Center) {
                Box(
                    modifier = Modifier
                        .size(32.dp)
                        .background(
                            if (isLocked) Locked else skillColor,
                            CircleShape
                        ),
                    contentAlignment = Alignment.Center
                ) {
                    if (isLocked) {
                        Icon(
                            imageVector = Icons.Default.Lock,
                            contentDescription = null,
                            tint = OnSurface.copy(alpha = 0.5f),
                            modifier = Modifier.size(16.dp)
                        )
                    } else if (status == TopicStatus.MASTERED) {
                        Icon(
                            imageVector = Icons.Default.Check,
                            contentDescription = null,
                            tint = Color.White,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = topic.name,
                    style = MaterialTheme.typography.titleMedium,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    color = if (isLocked) OnSurface.copy(alpha = 0.5f) else OnBackground
                )
                Text(
                    text = topic.status.label.uppercase(),
                    style = MaterialTheme.typography.labelSmall,
                    color = if (isLocked) OnSurface.copy(alpha = 0.5f) else skillColor,
                    letterSpacing = 1.sp
                )
            }

            if (!isLocked) {
                Text(
                    text = "L${topic.skillLevel}",
                    style = MaterialTheme.typography.labelSmall,
                    color = OnSurface,
                    modifier = Modifier
                        .background(SurfaceBright, MaterialTheme.shapes.small)
                        .padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
        }
    }
}

@Composable
fun KnowledgeNode(
    name: String,
    status: TopicStatus,
    modifier: Modifier = Modifier,
    onClick: () -> Unit = {}
) {
    val isLocked = status == TopicStatus.LOCKED

    Column(
        modifier = modifier.clickable(onClick = onClick),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            modifier = Modifier.size(64.dp),
            contentAlignment = Alignment.Center
        ) {
            Image(
                painter = painterResource(id = if (isLocked) R.drawable.ic_node_locked else R.drawable.ic_node_sun_amber),
                contentDescription = null,
                modifier = Modifier.fillMaxSize()
            )
        }

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = name,
            style = MaterialTheme.typography.labelSmall,
            color = if (isLocked) OnSurface.copy(alpha = 0.5f) else OnBackground,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis
        )
    }
}

@Composable
fun EmberChip(
    label: String,
    selected: Boolean,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Surface(
        modifier = modifier
            .clickable(onClick = onClick)
            .border(
                1.dp,
                if (selected) Primary else Outline,
                MaterialTheme.shapes.small
            ),
        shape = MaterialTheme.shapes.small,
        color = if (selected) Primary.copy(alpha = 0.1f) else Color.Transparent
    ) {
        Text(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            text = label.uppercase(),
            style = MaterialTheme.typography.labelSmall,
            color = if (selected) Primary else OnSurface,
            letterSpacing = 1.sp
        )
    }
}

@Composable
fun EmberTopBar(
    title: String,
    onBack: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {}
) {
    @OptIn(ExperimentalMaterial3Api::class)
    TopAppBar(
        title = {
            Text(
                text = title,
                style = MaterialTheme.typography.headlineMedium,
                color = OnBackground
            )
        },
        navigationIcon = {
            if (onBack != null) {
                IconButton(onClick = onBack) {
                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                        contentDescription = "Back",
                        tint = OnBackground
                    )
                }
            }
        },
        actions = actions,
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = Background,
            titleContentColor = OnBackground
        )
    )
}

@Composable
fun EmberShimmerCard(
    modifier: Modifier = Modifier,
    height: Int = 80
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .height(height.dp)
            .shimmerEffect(),
        shape = MaterialTheme.shapes.large,
        colors = CardDefaults.cardColors(containerColor = Surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {}
}

@Composable
fun AnimatedCountUpText(
    targetValue: Int,
    suffix: String = "%",
    style: androidx.compose.ui.text.TextStyle = MaterialTheme.typography.headlineLarge,
    color: Color = Primary
) {
    var displayValue by remember { mutableIntStateOf(0) }
    val animatedValue by animateIntAsState(
        targetValue = targetValue,
        animationSpec = tween(durationMillis = 800, easing = FastOutSlowInEasing),
        label = "count_up"
    )

    LaunchedEffect(animatedValue) {
        displayValue = animatedValue
    }

    Text(
        text = "$displayValue$suffix",
        style = style,
        color = color
    )
}
