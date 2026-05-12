package com.knowledgemap.app.ui.screen.home

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.NotificationsNone
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.knowledgemap.app.ui.components.*
import com.knowledgemap.app.ui.theme.*
import kotlinx.coroutines.launch

@Composable
fun HomeScreen(
    onTopicClick: (String) -> Unit = {},
    viewModel: HomeViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    Scaffold(
        topBar = {
            EmberTopBar(
                title = "Trang chủ",
                actions = {
                    IconButton(onClick = {
                        scope.launch {
                            snackbarHostState.showSnackbar("Thông báo: Chức năng đang được phát triển")
                        }
                    }) {
                        Icon(
                            imageVector = Icons.Default.NotificationsNone,
                            contentDescription = "Notifications",
                            tint = OnBackground
                        )
                    }
                }
            )
        },
        snackbarHost = { SnackbarHost(snackbarHostState) },
        containerColor = Background
    ) { padding ->
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
            contentPadding = PaddingValues(vertical = 16.dp)
        ) {
            item { MasteryProgressSection(masteryPercent = uiState.masteryPercent) }

            item {
                SectionHeader(title = "Gợi ý học tập")
            }

            if (uiState.isLoading) {
                item { EmberShimmerCard(height = 80) }
                item { EmberShimmerCard(height = 80) }
            } else {
                itemsIndexed(uiState.recommendations) { index, item ->
                    AnimatedVisibility(
                        visible = true,
                        enter = fadeIn(tween(300, delayMillis = index * 100)) +
                                expandVertically(tween(300, delayMillis = index * 100))
                    ) {
                        HomeRecommendationCard(item = item, onClick = { onTopicClick(item.topicId) })
                    }
                }
            }

            item {
                Spacer(modifier = Modifier.height(8.dp))
                SectionHeader(title = "Hoạt động gần đây")
            }

            if (uiState.isLoading) {
                item { EmberShimmerCard(height = 64) }
            } else {
                itemsIndexed(uiState.recentActivities) { index, item ->
                    AnimatedVisibility(
                        visible = true,
                        enter = fadeIn(tween(300, delayMillis = index * 80)) +
                                expandVertically(tween(300, delayMillis = index * 80))
                    ) {
                        HomeActivityCard(item = item)
                    }
                }
            }
        }
    }
}

@Composable
private fun MasteryProgressSection(masteryPercent: Int) {
    Column(
        modifier = Modifier.fillMaxWidth(),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(
            modifier = Modifier.size(160.dp),
            contentAlignment = Alignment.Center
        ) {
            val animatedProgress by animateFloatAsState(
                targetValue = masteryPercent / 100f,
                animationSpec = tween(durationMillis = 1500, easing = FastOutSlowInEasing),
                label = "arc_progress"
            )

            Canvas(modifier = Modifier.fillMaxSize()) {
                val strokeWidth = 12.dp.toPx()
                val radius = (size.minDimension - strokeWidth) / 2
                val topLeft = Offset(
                    (size.width - radius * 2) / 2,
                    (size.height - radius * 2) / 2
                )

                drawArc(
                    color = SurfaceBright,
                    startAngle = -90f,
                    sweepAngle = 360f,
                    useCenter = false,
                    topLeft = topLeft,
                    size = Size(radius * 2, radius * 2),
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                )

                drawArc(
                    color = Primary,
                    startAngle = -90f,
                    sweepAngle = 360f * animatedProgress,
                    useCenter = false,
                    topLeft = topLeft,
                    size = Size(radius * 2, radius * 2),
                    style = Stroke(width = strokeWidth, cap = StrokeCap.Round)
                )
            }

            AnimatedCountUpText(
                targetValue = masteryPercent,
                suffix = "%",
                style = MaterialTheme.typography.headlineLarge.copy(fontWeight = FontWeight.Bold),
                color = OnBackground
            )
        }

        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Bạn đang tiến bộ rất tốt!",
            style = MaterialTheme.typography.bodyLarge,
            color = OnBackground
        )
    }
}

@Composable
private fun SectionHeader(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.titleMedium,
        color = OnBackground,
        modifier = Modifier.padding(bottom = 12.dp)
    )
}

@Composable
private fun HomeRecommendationCard(item: HomeRecommendationItem, onClick: () -> Unit) {
    EmberCard(
        onClick = onClick,
        borderColor = if (item.level >= 2) Tertiary else Outline
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.title,
                    style = MaterialTheme.typography.titleSmall,
                    color = OnBackground
                )
                Text(
                    text = item.subtitle,
                    style = MaterialTheme.typography.bodyMedium,
                    color = OnSurface
                )
            }
            Surface(
                shape = MaterialTheme.shapes.small,
                color = SurfaceBright
            ) {
                Text(
                    text = "L${item.level}",
                    style = MaterialTheme.typography.labelSmall,
                    color = OnSurface,
                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                )
            }
        }
    }
}

@Composable
private fun HomeActivityCard(item: HomeActivityItem) {
    EmberCard {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = item.title,
                style = MaterialTheme.typography.titleSmall,
                color = OnBackground
            )
            Text(
                text = item.timeAgo,
                style = MaterialTheme.typography.labelSmall,
                color = OnSurface
            )
        }
    }
}