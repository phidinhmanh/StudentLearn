package com.knowledgemap.app.ui.screen.recommendation

import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.knowledgemap.app.ui.components.EmberCard
import com.knowledgemap.app.ui.components.EmberTopBar
import com.knowledgemap.app.ui.theme.*

@Composable
fun RecommendationScreen(
    onBack: () -> Unit,
    onTopicClick: (String) -> Unit,
    viewModel: RecommendationViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            EmberTopBar(
                title = "Nhiệm vụ",
                onBack = onBack
            )
        },
        containerColor = Background
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
        ) {
            when {
                uiState.isLoading -> {
                    CircularProgressIndicator(
                        modifier = Modifier.align(Alignment.Center),
                        color = Primary
                    )
                }
                uiState.error != null -> {
                    ErrorContent(error = uiState.error!!, onRetry = { viewModel.retry() })
                }
                uiState.recommendations.isEmpty() -> {
                    EmptyContent(onRetry = { viewModel.retry() })
                }
                else -> {
                    RecommendationList(
                        recommendations = uiState.recommendations,
                        onTopicClick = onTopicClick
                    )
                }
            }
        }
    }
}

@Composable
private fun RecommendationList(
    recommendations: List<com.knowledgemap.app.domain.model.Recommendation>,
    onTopicClick: (String) -> Unit
) {
    Column(modifier = Modifier.padding(16.dp)) {
        Text(
            text = "Dành cho bạn",
            style = MaterialTheme.typography.bodyMedium,
            color = OnSurface,
            modifier = Modifier.padding(bottom = 16.dp)
        )

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(16.dp),
            contentPadding = PaddingValues(bottom = 24.dp)
        ) {
            itemsIndexed(recommendations) { index, rec ->
                EmberRecommendationCard(
                    priority = index + 1,
                    topicName = rec.topic.name,
                    reason = rec.reason,
                    onStartAssessment = { onTopicClick(rec.topic.id) }
                )
            }
        }
    }
}

@Composable
private fun EmberRecommendationCard(
    priority: Int,
    topicName: String,
    reason: String,
    onStartAssessment: () -> Unit
) {
    EmberCard(
        borderColor = if (priority == 1) Primary else Outline
    ) {
        Column {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Surface(
                    modifier = Modifier
                        .size(32.dp)
                        .border(1.dp, Primary, MaterialTheme.shapes.small),
                    shape = MaterialTheme.shapes.small,
                    color = Primary.copy(alpha = 0.1f)
                ) {
                    Box(contentAlignment = Alignment.Center) {
                        Text(
                            text = "$priority",
                            color = Primary,
                            fontWeight = FontWeight.Bold,
                            style = MaterialTheme.typography.labelSmall
                        )
                    }
                }
                Text(
                    text = topicName,
                    style = MaterialTheme.typography.titleMedium,
                    color = OnBackground
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = reason,
                style = MaterialTheme.typography.bodyMedium,
                color = OnSurface
            )

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = onStartAssessment,
                modifier = Modifier.fillMaxWidth(),
                shape = MaterialTheme.shapes.small,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Primary,
                    contentColor = OnPrimary
                )
            ) {
                Icon(Icons.Default.PlayArrow, contentDescription = null)
                Text("Bắt đầu làm bài", modifier = Modifier.padding(start = 8.dp))
            }
        }
    }
}

@Composable
private fun ErrorContent(error: String, onRetry: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Đã xảy ra lỗi: $error",
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = Error
        )
        Spacer(modifier = Modifier.height(16.dp))
        OutlinedButton(onClick = onRetry, shape = MaterialTheme.shapes.small) {
            Icon(Icons.Default.Refresh, contentDescription = null)
            Text("Thử lại", modifier = Modifier.padding(start = 4.dp))
        }
    }
}

@Composable
private fun EmptyContent(onRetry: () -> Unit) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Chưa có gợi ý",
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center,
            color = Primary
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "Hoàn thành bài kiểm tra để nhận lộ trình học tập phù hợp.",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = OnSurface
        )
        Spacer(modifier = Modifier.height(32.dp))
        Button(
            onClick = onRetry,
            shape = MaterialTheme.shapes.small,
            colors = ButtonDefaults.buttonColors(containerColor = Primary, contentColor = OnPrimary)
        ) {
            Text("Tải lại")
        }
    }
}
