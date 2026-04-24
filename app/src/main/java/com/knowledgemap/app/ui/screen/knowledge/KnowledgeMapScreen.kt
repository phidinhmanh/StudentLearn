package com.knowledgemap.app.ui.screen.knowledge

import androidx.compose.foundation.background
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Lightbulb
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.knowledgemap.app.domain.model.TopicStatus
import com.knowledgemap.app.ui.components.LuminescentNode
import com.knowledgemap.app.ui.components.ModernCard
import com.knowledgemap.app.ui.components.ModernChip
import com.knowledgemap.app.ui.components.ModernTopicCard
import com.knowledgemap.app.ui.theme.Primary

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun KnowledgeMapScreen(
    onTopicClick: (String) -> Unit,
    onRecommendationsClick: () -> Unit,
    viewModel: KnowledgeMapViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    KnowledgeMapContent(
        uiState = uiState,
        onTopicClick = onTopicClick,
        onRecommendationsClick = onRecommendationsClick
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun KnowledgeMapContent(
    uiState: KnowledgeMapUiState,
    onTopicClick: (String) -> Unit,
    onRecommendationsClick: () -> Unit
) {
    var selectedFilter by remember { mutableStateOf<Int?>(null) }

    val filteredTopics = if (selectedFilter != null) {
        uiState.topics.filter { it.skillLevel == selectedFilter }
    } else {
        uiState.topics
    }

    val topicsByChapter = filteredTopics.groupBy { it.chapter }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Text(
                        "KNOWLEDGE CONSTELLATION", 
                        style = MaterialTheme.typography.labelLarge,
                        fontWeight = FontWeight.Bold,
                        letterSpacing = 2.sp
                    ) 
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.background,
                    titleContentColor = MaterialTheme.colorScheme.onBackground
                )
            )
        }
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(MaterialTheme.colorScheme.background)
        ) {
            // Constellation Map Visual (Horizontal Scroll of Nodes)
            Text(
                "CORE MODULES",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f),
                modifier = Modifier.padding(start = 16.dp, top = 8.dp),
                letterSpacing = 1.sp
            )
            
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(140.dp)
                    .horizontalScroll(rememberScrollState())
                    .padding(vertical = 16.dp),
                horizontalArrangement = Arrangement.spacedBy(24.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Spacer(modifier = Modifier.width(0.dp))
                uiState.topics.take(5).forEach { topic ->
                    LuminescentNode(
                        name = topic.name,
                        status = topic.status,
                        onClick = { onTopicClick(topic.id) }
                    )
                }
                Spacer(modifier = Modifier.width(16.dp))
            }

            // Filter Section
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 16.dp, vertical = 8.dp),
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                ModernChip(
                    selected = selectedFilter == null,
                    onClick = { selectedFilter = null },
                    label = "Tất cả"
                )
                TopicStatus.values().forEach { status ->
                    ModernChip(
                        selected = selectedFilter == status.level,
                        onClick = { selectedFilter = status.level },
                        label = status.label
                    )
                }
            }

            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                // Progress Overview Item
                item {
                    ModernCard(
                        borderColor = Primary.copy(alpha = 0.3f)
                    ) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.SpaceBetween
                        ) {
                            Column {
                                Text(
                                    text = "DATA SYNC COMPLETE",
                                    style = MaterialTheme.typography.labelSmall,
                                    color = Primary,
                                    letterSpacing = 1.sp
                                )
                                Text(
                                    text = "${uiState.progressPercent}% MASTERY",
                                    style = MaterialTheme.typography.headlineMedium,
                                    fontWeight = FontWeight.Bold
                                )
                            }
                            IconButton(onClick = onRecommendationsClick) {
                                Icon(
                                    Icons.Default.AutoAwesome, 
                                    contentDescription = null,
                                    tint = Primary
                                )
                            }
                        }
                    }
                }

                topicsByChapter.forEach { (chapter, topics) ->
                    item {
                        chapter?.let {
                            Text(
                                text = it.uppercase(),
                                style = MaterialTheme.typography.labelSmall,
                                fontWeight = FontWeight.Bold,
                                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f),
                                modifier = Modifier.padding(top = 16.dp, bottom = 8.dp, start = 4.dp),
                                letterSpacing = 2.sp
                            )
                        }
                    }

                    items(topics) { topic ->
                        ModernTopicCard(
                            topic = topic,
                            onClick = { onTopicClick(topic.id) }
                        )
                    }
                }
            }
        }
    }
}
