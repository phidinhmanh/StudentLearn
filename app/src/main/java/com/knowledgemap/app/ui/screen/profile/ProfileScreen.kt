package com.knowledgemap.app.ui.screen.profile

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.MoreVert
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.knowledgemap.app.R
import com.knowledgemap.app.domain.model.DegradationTier
import com.knowledgemap.app.domain.usecase.DegradationCalculator
import com.knowledgemap.app.ui.components.*
import com.knowledgemap.app.ui.theme.*

@Composable
fun ProfileScreen() {
    var showEditSheet by remember { mutableStateOf(false) }
    var showFileMenu by remember { mutableStateOf(false) }

    // Spring animation for bottom sheet
    val animatedProgress by animateFloatAsState(
        targetValue = if (showEditSheet) 1f else 0f,
        animationSpec = spring(
            dampingRatio = Spring.DampingRatioMediumBouncy,
            stiffness = Spring.StiffnessMedium
        ),
        label = "sheet_offset"
    )

    Box(modifier = Modifier.fillMaxSize()) {
        Scaffold(
            topBar = {
                EmberTopBar(
                    title = "Hồ sơ năng lực",
                    actions = {
                        IconButton(onClick = { /* settings */ }) {
                            Icon(
                                imageVector = Icons.Default.Settings,
                                contentDescription = "Settings",
                                tint = OnBackground
                            )
                        }
                    }
                )
            },
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
                item { ProfileHeader(onAvatarClick = { showEditSheet = true }) }

                item {
                    AnimatedStatsRow(mastery = 72, daysLearned = 142, topicsLearned = 58)
                }

                item {
                    val calc = remember { DegradationCalculator() }
                    val mastery = 0.72
                    val daysSinceLastStudy = 1
                    val streakDays = 7
                    val currentD = calc.calculate(mastery, daysSinceLastStudy)
                    val tier = DegradationTier.fromDegradationValue(currentD)
                    AnimatedDegradationMemeCard(
                        tier = tier,
                        currentD = currentD,
                        mastery = mastery,
                        daysSinceLastStudy = daysSinceLastStudy,
                        streakDays = streakDays
                    )
                }

                item {
                    AnimatedSectionTitle("Thành tích")
                }

                item {
                    AnimatedBadgeRow()
                }

                item {
                    AnimatedSectionTitle("Kho tài liệu của tôi")
                }

                itemsIndexed(
                    listOf(
                        DocumentItem("Toan_10_GK1.pdf", true),
                        DocumentItem("Ly_10_Chuong_1.pdf", false)
                    )
                ) { index, doc ->
                    AnimatedVisibility(
                        visible = true,
                        enter = slideInHorizontally(
                            initialOffsetX = { -it },
                            animationSpec = tween(300, delayMillis = index * 80)
                        ) + fadeIn(tween(300, delayMillis = index * 80))
                    ) {
                        DocumentCard(
                            item = doc,
                            onMenuClick = { showFileMenu = true }
                        )
                    }
                }

                item {
                    AnimatedSectionTitle("Cài đặt")
                }

                item {
                    SettingsCard()
                }
            }
        }

        // Dimmed overlay + Bottom sheet with spring
        AnimatedVisibility(
            visible = showEditSheet,
            enter = fadeIn(tween(300)),
            exit = fadeOut(tween(300))
        ) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.5f * animatedProgress))
                    .clickable { showEditSheet = false }
            ) {
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .align(Alignment.BottomCenter)
                        .offset(y = ((1f - animatedProgress) * 400).dp),
                    shape = MaterialTheme.shapes.large,
                    color = Surface,
                    shadowElevation = 8.dp
                ) {
                    Column(modifier = Modifier.padding(24.dp)) {
                        Text(
                            "Chỉnh sửa hồ sơ",
                            style = MaterialTheme.typography.titleMedium,
                            color = OnBackground
                        )
                        Spacer(modifier = Modifier.height(16.dp))
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(12.dp)
                        ) {
                            Image(
                                painter = painterResource(id = R.drawable.ic_user_avatar_astro),
                                contentDescription = "Avatar",
                                modifier = Modifier.size(48.dp)
                            )
                            Text("Thay đổi ảnh đại diện", color = OnSurface)
                        }
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(
                            onClick = { showEditSheet = false },
                            modifier = Modifier.fillMaxWidth()
                        ) {
                            Text("Đóng")
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun ProfileHeader(onAvatarClick: () -> Unit) {
    EmberCard(
        modifier = Modifier.clickable { onAvatarClick() }
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Image(
                painter = painterResource(id = R.drawable.ic_user_avatar_astro),
                contentDescription = "Avatar",
                modifier = Modifier.size(64.dp)
            )
            Column {
                Text(
                    text = "Học sinh",
                    style = MaterialTheme.typography.headlineMedium,
                    color = OnBackground
                )
                Text(
                    text = "Level 12",
                    style = MaterialTheme.typography.labelSmall,
                    color = Secondary
                )
            }
        }
    }
}

@Composable
private fun AnimatedStatsRow(mastery: Int, daysLearned: Int, topicsLearned: Int) {
    val stats = listOf(
        StatData(mastery.toFloat(), "Mastery"),
        StatData(daysLearned.toFloat(), "Ngày học"),
        StatData(topicsLearned.toFloat(), "Chủ đề")
    )

    Column(modifier = Modifier.fillMaxWidth()) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            stats.forEachIndexed { index, stat ->
                AnimatedVisibility(
                    visible = true,
                    enter = fadeIn(tween(300, delayMillis = index * 100)) +
                            slideInHorizontally(tween(300, delayMillis = index * 100)) { it / 2 }
                ) {
                    when (index) {
                        1 -> StatBoxWithIcon(
                            stat = stat,
                            iconRes = R.drawable.ic_streak_fire
                        )
                        else -> StatBox(stat = stat)
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))

        // XP / Progress Bar
        val xpProgress by animateFloatAsState(
            targetValue = mastery / 100f,
            animationSpec = tween(1200, easing = FastOutSlowInEasing),
            label = "xp_bar"
        )

        LinearProgressIndicator(
            progress = { xpProgress },
            modifier = Modifier
                .fillMaxWidth()
                .height(4.dp),
            color = Secondary,
            trackColor = SurfaceBright
        )
    }
}

@Composable
private fun StatBox(stat: StatData) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        AnimatedCountUpText(
            targetValue = stat.value.toInt(),
            suffix = if (stat.label == "Mastery") "%" else "",
            style = MaterialTheme.typography.titleMedium,
            color = Primary
        )
        Text(text = stat.label, style = MaterialTheme.typography.labelSmall, color = OnSurface)
    }
}

@Composable
private fun StatBoxWithIcon(stat: StatData, iconRes: Int) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Image(
                painter = painterResource(id = iconRes),
                contentDescription = null,
                modifier = Modifier.size(20.dp).padding(end = 4.dp)
            )
            AnimatedCountUpText(
                targetValue = stat.value.toInt(),
                style = MaterialTheme.typography.titleMedium,
                color = Primary
            )
        }
        Text(text = stat.label, style = MaterialTheme.typography.labelSmall, color = OnSurface)
    }
}

private data class StatData(val value: Float, val label: String)

@Composable
private fun AnimatedSectionTitle(title: String) {
    Text(
        text = title,
        style = MaterialTheme.typography.titleMedium,
        color = OnBackground,
        modifier = Modifier.padding(bottom = 12.dp)
    )
}

@Composable
private fun AnimatedBadgeRow() {
    val badges = listOf(
        R.drawable.ic_badge_rank_1,
        R.drawable.ic_badge_silver,
        R.drawable.ic_badge_bronze
    )

    EmberCard {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceEvenly
        ) {
            badges.forEachIndexed { index, res ->
                AnimatedVisibility(
                    visible = true,
                    enter = scaleIn(
                        animationSpec = spring(
                            dampingRatio = Spring.DampingRatioMediumBouncy,
                            stiffness = 300f
                        ),
                        initialScale = 0f
                    ) + fadeIn(tween(200, delayMillis = index * 100))
                ) {
                    Image(
                        painter = painterResource(id = res),
                        contentDescription = null,
                        modifier = Modifier.size(48.dp)
                    )
                }
            }
        }
    }
}

data class DocumentItem(val name: String, val isAnalyzed: Boolean)

@Composable
private fun DocumentCard(item: DocumentItem, onMenuClick: () -> Unit) {
    EmberCard(
        onClick = { /* open document detail */ }
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = item.name,
                    style = MaterialTheme.typography.titleSmall,
                    color = OnBackground
                )
                Text(
                    text = if (item.isAnalyzed) "Đã phân tích xong" else "Đang xử lý...",
                    style = MaterialTheme.typography.labelSmall,
                    color = if (item.isAnalyzed) Secondary else OnSurface
                )
            }
            IconButton(onClick = onMenuClick) {
                Icon(
                    imageVector = Icons.Default.MoreVert,
                    contentDescription = "Menu",
                    tint = OnSurface
                )
            }
        }
    }
}

@Composable
private fun SettingsCard() {
    var notificationsEnabled by remember { mutableStateOf(true) }
    val trackColor by animateColorAsState(
        targetValue = if (notificationsEnabled) Primary else Disabled,
        label = "switch_track"
    )

    EmberCard {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text("Thông báo nhắc học", style = MaterialTheme.typography.bodyLarge, color = OnBackground)
            Switch(
                checked = notificationsEnabled,
                onCheckedChange = { notificationsEnabled = it },
                colors = SwitchDefaults.colors(
                    checkedThumbColor = OnPrimary,
                    checkedTrackColor = trackColor,
                    uncheckedThumbColor = OnSurface,
                    uncheckedTrackColor = SurfaceBright
                )
            )
        }
    }
}