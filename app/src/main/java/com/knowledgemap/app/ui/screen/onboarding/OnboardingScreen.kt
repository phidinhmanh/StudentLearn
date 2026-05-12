package com.knowledgemap.app.ui.screen.onboarding

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.pager.HorizontalPager
import androidx.compose.foundation.pager.rememberPagerState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Lightbulb
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Route
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.paint
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.knowledgemap.app.R
import com.knowledgemap.app.ui.components.EmberChip
import com.knowledgemap.app.ui.theme.*
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch

private val features = listOf(
    Feature(
        icon = Icons.Default.Lightbulb,
        title = "Phát hiện lỗ hổng",
        description = "AI phân tích kiến thức của bạn và tìm ra điểm yếu"
    ),
    Feature(
        icon = Icons.Default.Route,
        title = "Tối ưu lộ trình",
        description = "Gợi ý bài học phù hợp nhất với trình độ hiện tại"
    ),
    Feature(
        icon = Icons.Default.Map,
        title = "Bản đồ tri thức",
        description = "Xem toàn bộ kiến thức dưới dạng sơ đồ trực quan"
    )
)

private data class Feature(
    val icon: ImageVector,
    val title: String,
    val description: String
)

@OptIn(ExperimentalFoundationApi::class)
@Composable
fun OnboardingScreen(
    onComplete: () -> Unit,
    viewModel: OnboardingViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var showGoalSelection by remember { mutableStateOf(false) }
    val pagerState = rememberPagerState(pageCount = { features.size })

    // Logo entrance animation
    var logoVisible by remember { mutableStateOf(false) }
    LaunchedEffect(Unit) {
        logoVisible = true
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .paint(
                painter = painterResource(id = R.drawable.bg_nebula_orange),
                contentScale = ContentScale.Crop
            )
    ) {
        if (!showGoalSelection) {
            OnboardingIntro(
                pagerState = pagerState,
                logoVisible = logoVisible,
                onNext = { showGoalSelection = true }
            )
        } else {
            GoalSelection(onComplete = onComplete)
        }

        // Animated dot indicators
        AnimatedContent(
            targetState = !showGoalSelection,
            transitionSpec = {
                fadeIn(tween(300)) togetherWith fadeOut(tween(300))
            },
            label = "dots"
        ) { showIntro ->
            Row(
                modifier = Modifier
                    .align(Alignment.BottomCenter)
                    .padding(bottom = 32.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                if (showIntro) {
                    repeat(features.size) { index ->
                        val isActive = pagerState.currentPage == index
                        val color by animateColorAsState(
                            targetValue = if (isActive) Primary else Disabled,
                            animationSpec = tween(300),
                            label = "dot_$index"
                        )
                        Box(
                            modifier = Modifier
                                .size(if (isActive) 10.dp else 8.dp)
                                .background(color, CircleShape)
                        )
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun OnboardingIntro(
    pagerState: androidx.compose.foundation.pager.PagerState,
    logoVisible: Boolean,
    onNext: () -> Unit
) {
    // Logo scale/fade animation
    val logoScale by animateFloatAsState(
        targetValue = if (logoVisible) 1f else 0.8f,
        animationSpec = tween(durationMillis = 600, easing = FastOutSlowInEasing),
        label = "logo_scale"
    )
    val logoAlpha by animateFloatAsState(
        targetValue = if (logoVisible) 1f else 0f,
        animationSpec = tween(durationMillis = 600, easing = FastOutSlowInEasing),
        label = "logo_alpha"
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        // Logo
        Image(
            painter = painterResource(id = R.drawable.ic_ember_logo_main),
            contentDescription = "Ember Logo",
            modifier = Modifier
                .size(100.dp)
                .scale(logoScale)
                .graphicsLayer { alpha = logoAlpha }
        )

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "EMBER",
            style = MaterialTheme.typography.headlineLarge,
            color = Primary,
            letterSpacing = 4.sp
        )

        Spacer(modifier = Modifier.height(4.dp))

        Text(
            text = "Trợ lý học tập thông minh",
            style = MaterialTheme.typography.bodyMedium,
            color = OnSurface
        )

        Spacer(modifier = Modifier.height(32.dp))

        // Swipeable feature pager
        HorizontalPager(
            state = pagerState,
            modifier = Modifier.fillMaxWidth()
        ) { page ->
            FeaturePage(feature = features[page])
        }

        Spacer(modifier = Modifier.height(32.dp))

        // CTA Button with press animation
        var isPressed by remember { mutableStateOf(false) }
        val buttonScale by animateFloatAsState(
            targetValue = if (isPressed) 0.95f else 1f,
            animationSpec = spring(dampingRatio = Spring.DampingRatioMediumBouncy),
            label = "button_scale"
        )

val scope = rememberCoroutineScope()

        Button(
            onClick = {
                if (pagerState.currentPage < features.size - 1) {
                    scope.launch {
                        pagerState.animateScrollToPage(pagerState.currentPage + 1)
                    }
                } else {
                    onNext()
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .scale(buttonScale),
            shape = MaterialTheme.shapes.small,
            colors = ButtonDefaults.buttonColors(
                containerColor = Primary,
                contentColor = OnPrimary
            )
        ) {
            Text(
                text = "BẮT ĐẦU NGAY",
                style = MaterialTheme.typography.labelLarge,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }
    }
}

@Composable
private fun FeaturePage(feature: Feature) {
    var visible by remember { mutableStateOf(false) }
    val animatedAlpha by animateFloatAsState(
        targetValue = if (visible) 1f else 0f,
        animationSpec = tween(400),
        label = "feature_alpha"
    )
    val animatedY by animateFloatAsState(
        targetValue = if (visible) 0f else 10f,
        animationSpec = tween(400),
        label = "feature_y"
    )

    LaunchedEffect(feature) {
        delay(100)
        visible = true
    }

    Row(
        modifier = Modifier
            .fillMaxWidth()
            .graphicsLayer {
                alpha = animatedAlpha
                translationY = animatedY
            },
        verticalAlignment = Alignment.Top,
        horizontalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Icon(
            imageVector = feature.icon,
            contentDescription = null,
            tint = Primary,
            modifier = Modifier.size(32.dp)
        )
        Column {
            Text(
                text = feature.title,
                style = MaterialTheme.typography.titleMedium,
                color = OnBackground
            )
            Text(
                text = feature.description,
                style = MaterialTheme.typography.bodyMedium,
                color = OnSurface
            )
        }
    }
}

@Composable
private fun GoalSelection(onComplete: () -> Unit) {
    val goals = listOf(
        "Lấy gốc kiến thức", "Ôn thi", "Nâng cao kỹ năng",
        "Mở rộng kiến thức", "Chuẩn bị đại học", "Giải bài khó"
    )
    val selectedGoals = remember { mutableStateListOf<String>() }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Spacer(modifier = Modifier.height(64.dp))

        Text(
            text = "Mục tiêu của bạn là gì?",
            style = MaterialTheme.typography.headlineMedium,
            textAlign = TextAlign.Center,
            color = OnBackground
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Chọn ít nhất một mục tiêu để cá nhân hóa trải nghiệm học tập.",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = OnSurface
        )

        Spacer(modifier = Modifier.height(48.dp))

        FlowRow(
            modifier = Modifier.fillMaxWidth(),
            mainAxisSpacing = 8.dp,
            crossAxisSpacing = 12.dp
        ) {
            goals.forEach { goal ->
                EmberChip(
                    label = goal,
                    selected = selectedGoals.contains(goal),
                    onClick = {
                        if (selectedGoals.contains(goal)) {
                            selectedGoals.remove(goal)
                        } else {
                            selectedGoals.add(goal)
                        }
                    }
                )
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        Button(
            onClick = onComplete,
            enabled = selectedGoals.isNotEmpty(),
            modifier = Modifier.fillMaxWidth(),
            shape = MaterialTheme.shapes.small,
            colors = ButtonDefaults.buttonColors(
                containerColor = Primary,
                contentColor = OnPrimary,
                disabledContainerColor = Disabled,
                disabledContentColor = OnSurface.copy(alpha = 0.5f)
            )
        ) {
            Text(
                text = "Hoàn tất",
                style = MaterialTheme.typography.labelLarge,
                modifier = Modifier.padding(vertical = 8.dp)
            )
        }

        Spacer(modifier = Modifier.height(48.dp))
    }
}

@Composable
fun FlowRow(
    modifier: Modifier = Modifier,
    mainAxisSpacing: androidx.compose.ui.unit.Dp = 0.dp,
    crossAxisSpacing: androidx.compose.ui.unit.Dp = 0.dp,
    content: @Composable () -> Unit
) {
    androidx.compose.ui.layout.Layout(
        content = content,
        modifier = modifier
    ) { measurables, constraints ->
        val placeables = measurables.map { it.measure(constraints.copy(minWidth = 0, minHeight = 0)) }
        val rows = mutableListOf<List<androidx.compose.ui.layout.Placeable>>()
        var currentRow = mutableListOf<androidx.compose.ui.layout.Placeable>()
        var currentRowWidth = 0

        placeables.forEach { placeable ->
            if (currentRowWidth + placeable.width + mainAxisSpacing.roundToPx() > constraints.maxWidth && currentRow.isNotEmpty()) {
                rows.add(currentRow)
                currentRow = mutableListOf()
                currentRowWidth = 0
            }
            currentRow.add(placeable)
            currentRowWidth += placeable.width + mainAxisSpacing.roundToPx()
        }
        rows.add(currentRow)

        val height = rows.sumOf { row -> row.maxOf { it.height } } + (rows.size - 1) * crossAxisSpacing.roundToPx()
        layout(constraints.maxWidth, height) {
            var y = 0
            rows.forEach { row ->
                var x = 0
                val rowHeight = row.maxOf { it.height }
                row.forEach { placeable ->
                    placeable.placeRelative(x, y)
                    x += placeable.width + mainAxisSpacing.roundToPx()
                }
                y += rowHeight + crossAxisSpacing.roundToPx()
            }
        }
    }
}