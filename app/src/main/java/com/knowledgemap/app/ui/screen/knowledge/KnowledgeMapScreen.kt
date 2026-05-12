package com.knowledgemap.app.ui.screen.knowledge


import androidx.compose.animation.core.*

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.rememberTransformableState
import androidx.compose.foundation.gestures.transformable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.paint
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.PathEffect
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.knowledgemap.app.R
import com.knowledgemap.app.domain.model.TopicStatus
import com.knowledgemap.app.ui.components.*
import com.knowledgemap.app.ui.theme.*
import kotlinx.coroutines.launch

@Composable
fun KnowledgeMapScreen(
    onTopicClick: (String) -> Unit,
    onRecommendationsClick: () -> Unit,
    viewModel: KnowledgeMapViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()

    KnowledgeMapContent(
        uiState = uiState,
        onTopicClick = onTopicClick,
        onRecommendationsClick = onRecommendationsClick,
        onSearchClick = {
            scope.launch {
                snackbarHostState.showSnackbar("Tìm kiếm: Chức năng đang được phát triển")
            }
        },
        snackbarHostState = snackbarHostState
    )
}

@Composable
fun KnowledgeMapContent(
    uiState: KnowledgeMapUiState,
    onTopicClick: (String) -> Unit,
    onRecommendationsClick: () -> Unit,
    onSearchClick: () -> Unit = {},
    snackbarHostState: SnackbarHostState = remember { SnackbarHostState() }
) {
    val haptic = androidx.compose.ui.platform.LocalHapticFeedback.current
    var selectedFilter by remember { mutableStateOf<Int?>(null) }
    val scope = rememberCoroutineScope()

    val filteredTopics = if (selectedFilter != null) {
        uiState.topics.filter { it.skillLevel == selectedFilter }
    } else {
        uiState.topics
    }

    val topicsByChapter = filteredTopics.groupBy { it.chapter }

    // Transformation states
    var scale by remember { mutableFloatStateOf(1f) }
    var offset by remember { mutableStateOf(Offset.Zero) }
    val transformState = rememberTransformableState { zoomChange, offsetChange, _ ->
        scale = (scale * zoomChange).coerceIn(0.5f, 3f)
        offset += offsetChange
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .paint(
                painter = painterResource(id = R.drawable.bg_grid_space),
                contentScale = ContentScale.Crop
            )
    ) {
        Scaffold(
            topBar = {
                EmberTopBar(
                    title = "Sơ đồ Tri thức",
                    actions = {
                        IconButton(onClick = onSearchClick) {
                            Icon(Icons.Default.Search, contentDescription = "Tìm kiếm", tint = OnBackground)
                        }
                    }
                )
            },
            snackbarHost = { SnackbarHost(snackbarHostState) },
            containerColor = Color.Transparent
        ) { padding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                // Graph Hero Section
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(200.dp)
                ) {
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .transformable(state = transformState)
                    ) {
                        // Node Layout with lines
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .graphicsLayer(
                                    scaleX = scale,
                                    scaleY = scale,
                                    translationX = offset.x,
                                    translationY = offset.y
                                )
                        ) {
                            // Drawing connecting lines
                            val edgeProgress by animateFloatAsState(
                                targetValue = 1f,
                                animationSpec = tween(1500, easing = LinearOutSlowInEasing),
                                label = "edge_draw"
                            )

                            Canvas(modifier = Modifier.fillMaxSize()) {
                                // Dummy connections for demo
                                val path = Path().apply {
                                    moveTo(100f, 100f)
                                    quadraticBezierTo(200f, 150f, 300f, 100f)
                                    lineTo(400f, 200f)
                                }
                                drawPath(
                                    path = path,
                                    color = Primary.copy(alpha = 0.4f),
                                    style = Stroke(
                                        width = 2.dp.toPx(),
                                        pathEffect = PathEffect.dashPathEffect(
                                            floatArrayOf(20f, 10f),
                                            phase = edgeProgress * 100f
                                        )
                                    )
                                )
                            }

                            // Nodes
                            uiState.topics.take(6).forEachIndexed { index, topic ->
                                var isClicked by remember { mutableStateOf(false) }
                                val nodeScale by animateFloatAsState(
                                    targetValue = if (isClicked) 1.2f else 1f,
                                    label = "node_scale"
                                )
                                val glowAlpha by animateFloatAsState(
                                    targetValue = if (isClicked) 0.6f else 0f,
                                    label = "glow_alpha"
                                )

                                Box(
                                    modifier = Modifier
                                        .offset(x = (index * 80).dp, y = (if (index % 2 == 0) 40 else 100).dp)
                                        .scale(nodeScale)
                                ) {
                                    // Glow effect behind node
                                    if (isClicked) {
                                        Box(
                                            modifier = Modifier
                                                .size(80.dp)
                                                .align(Alignment.Center)
                                                .background(
                                                    color = Primary.copy(alpha = glowAlpha),
                                                    shape = androidx.compose.foundation.shape.CircleShape
                                                )
                                        )
                                    }
                                    KnowledgeNode(
                                        name = topic.name,
                                        status = topic.status,
                                        onClick = {
                                            onTopicClick(topic.id)
                                        }
                                    )
                                }
                            }
                        }
                    }

                    // Zoom controls overlay - inside Graph Box
                    Row(
                        modifier = Modifier
                            .align(Alignment.BottomEnd)
                            .padding(8.dp)
                            .background(Surface.copy(alpha = 0.7f), MaterialTheme.shapes.small),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        IconButton(onClick = { scale = (scale + 0.2f).coerceAtMost(3f) }, modifier = Modifier.size(32.dp)) {
                            Icon(Icons.Default.Add, contentDescription = "Zoom in", tint = OnBackground, modifier = Modifier.size(18.dp))
                        }
                        IconButton(onClick = { scale = (scale - 0.2f).coerceAtLeast(0.5f) }, modifier = Modifier.size(32.dp)) {
                            Icon(Icons.Default.Remove, contentDescription = "Zoom out", tint = OnBackground, modifier = Modifier.size(18.dp))
                        }
                        IconButton(onClick = {
                            scale = 1f
                            offset = Offset.Zero
                        }, modifier = Modifier.size(32.dp)) {
                            Icon(Icons.Default.CenterFocusStrong, contentDescription = "Center", tint = OnBackground, modifier = Modifier.size(18.dp))
                        }
                    }
                }

                // Filter chips
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .horizontalScroll(rememberScrollState())
                        .padding(horizontal = 16.dp, vertical = 8.dp),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    EmberChip(
                        selected = selectedFilter == null,
                        onClick = { selectedFilter = null },
                        label = "Tất cả"
                    )
                    TopicStatus.values().forEach { status ->
                        EmberChip(
                            selected = selectedFilter == status.level,
                            onClick = { selectedFilter = status.level },
                            label = status.label
                        )
                    }
                }

                // Topic List
                LazyColumn(
                    modifier = Modifier
                        .fillMaxWidth()
                        .weight(1f),
                    contentPadding = PaddingValues(start = 16.dp, end = 16.dp, top = 8.dp, bottom = 24.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    // Progress card - taking ~35% of viewport height
                    item {
                        EmberCard(
                            modifier = Modifier.fillParentMaxHeight(0.35f),
                            containerColor = Surface.copy(alpha = 0.85f)
                        ) {
                            Row(
                                modifier = Modifier.fillMaxSize(),
                                verticalAlignment = Alignment.CenterVertically,
                                horizontalArrangement = Arrangement.SpaceBetween
                            ) {
                                Column(
                                    modifier = Modifier.weight(1f),
                                    verticalArrangement = Arrangement.Center
                                ) {
                                    Text(
                                        text = "Tiến độ tổng thể",
                                        style = MaterialTheme.typography.titleMedium,
                                        color = OnSurface
                                    )
                                    Spacer(modifier = Modifier.height(8.dp))
                                    AnimatedCountUpText(
                                        targetValue = uiState.progressPercent,
                                        style = MaterialTheme.typography.displayLarge.copy(fontWeight = FontWeight.Bold)
                                    )
                                    Spacer(modifier = Modifier.height(8.dp))
                                    Text(
                                        text = "Hoàn thành: ${uiState.completedCount}/${uiState.totalCount} bài học",
                                        style = MaterialTheme.typography.bodyLarge,
                                        color = OnSurface.copy(alpha = 0.7f)
                                    )
                                }
                                IconButton(
                                    onClick = {
                                        haptic.performHapticFeedback(androidx.compose.ui.hapticfeedback.HapticFeedbackType.LongPress)
                                        onRecommendationsClick()
                                    },
                                    modifier = Modifier.size(56.dp)
                                ) {
                                    Icon(
                                        Icons.Default.AutoAwesome,
                                        contentDescription = "Gợi ý",
                                        tint = Primary,
                                        modifier = Modifier.size(36.dp)
                                    )
                                }
                            }
                        }
                    }

                    topicsByChapter.forEach { (chapter, topics) ->
                        item {
                            Text(
                                text = chapter,
                                style = MaterialTheme.typography.titleSmall,
                                color = OnBackground,
                                modifier = Modifier.padding(top = 16.dp, bottom = 8.dp, start = 4.dp)
                            )
                        }
                        items(topics) { topic ->
                            EmberListItem(
                                topic = topic,
                                onClick = { onTopicClick(topic.id) }
                            )
                        }
                    }
                }
            }
        }
    }
}
