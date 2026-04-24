package com.knowledgemap.app.ui.screen.recommendation

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.itemsIndexed
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.knowledgemap.app.ui.components.ModernCard
import com.knowledgemap.app.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecommendationScreen(
    onBack: () -> Unit,
    onTopicClick: (String) -> Unit,
    viewModel: RecommendationViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { 
                    Text(
                        "OPTIMIZED PATHWAY", 
                        style = MaterialTheme.typography.labelLarge,
                        letterSpacing = 2.sp
                    ) 
                },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, "Back")
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.background,
                    titleContentColor = MaterialTheme.colorScheme.onBackground
                )
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .background(MaterialTheme.colorScheme.background)
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
            text = "SYSTEM ANALYSIS DETECTED KNOWLEDGE GAPS. INITIALIZING REMEDIATION PATHWAY:",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f),
            modifier = Modifier.padding(bottom = 16.dp),
            letterSpacing = 1.sp
        )

        LazyColumn(
            verticalArrangement = Arrangement.spacedBy(16.dp),
            contentPadding = PaddingValues(bottom = 24.dp)
        ) {
            itemsIndexed(recommendations) { index, rec ->
                ModernRecommendationCard(
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
private fun ModernRecommendationCard(
    priority: Int,
    topicName: String,
    reason: String,
    onStartAssessment: () -> Unit
) {
    ModernCard(
        borderColor = if (priority == 1) Primary.copy(alpha = 0.5f) else MaterialTheme.colorScheme.outline.copy(alpha = 0.2f)
    ) {
        Column {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                Surface(
                    modifier = Modifier
                        .size(32.dp)
                        .border(1.dp, Primary, MaterialTheme.shapes.medium),
                    shape = MaterialTheme.shapes.medium,
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
                    text = topicName.uppercase(),
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    letterSpacing = 1.sp
                )
            }

            Spacer(modifier = Modifier.height(12.dp))

            Text(
                text = reason,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.7f)
            )

            Spacer(modifier = Modifier.height(16.dp))

            Button(
                onClick = onStartAssessment,
                modifier = Modifier.fillMaxWidth(),
                shape = MaterialTheme.shapes.medium,
                colors = ButtonDefaults.buttonColors(
                    containerColor = Primary,
                    contentColor = OnPrimary
                )
            ) {
                Icon(Icons.Default.PlayArrow, contentDescription = null)
                Text("INITIALIZE ASSESSMENT", modifier = Modifier.padding(start = 8.dp))
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
            text = "CRITICAL ERROR: $error",
            style = MaterialTheme.typography.bodyLarge,
            textAlign = TextAlign.Center,
            color = Error
        )
        Spacer(modifier = Modifier.height(16.dp))
        OutlinedButton(onClick = onRetry, shape = MaterialTheme.shapes.medium) {
            Icon(Icons.Default.Refresh, contentDescription = null)
            Text("RETRY SYNC", modifier = Modifier.padding(start = 4.dp))
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
            text = "NO RECOMMENDATIONS FOUND",
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center,
            color = Primary
        )
        Spacer(modifier = Modifier.height(16.dp))
        Text(
            text = "COMPLETE PRELIMINARY ASSESSMENTS TO GENERATE OPTIMIZED LEARNING PATHWAYS.",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
            letterSpacing = 1.sp
        )
        Spacer(modifier = Modifier.height(32.dp))
        Button(onClick = onRetry, shape = MaterialTheme.shapes.medium) {
            Text("REFRESH DATA")
        }
    }
}

