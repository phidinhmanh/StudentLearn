package com.knowledgemap.app.ui.screen.assessment

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.knowledgemap.app.ui.theme.*

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AssessmentScreen(
    topicId: String,
    onBack: () -> Unit,
    onComplete: () -> Unit,
    viewModel: AssessmentViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    LaunchedEffect(topicId) {
        viewModel.loadQuiz(topicId)
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        uiState.topicName.uppercase().ifEmpty { "ASSESSMENT" },
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

                uiState.showResults -> {
                    ResultsContent(
                        score = uiState.score,
                        total = uiState.totalQuestions,
                        skillBefore = uiState.skillBefore,
                        skillAfter = uiState.skillAfter,
                        answers = uiState.answers,
                        questions = uiState.questions,
                        onComplete = onComplete
                    )
                }

                uiState.questions.isNotEmpty() -> {
                    val safeIndex = uiState.currentIndex.coerceIn(0, uiState.questions.size - 1)
                    QuizContent(
                        currentIndex = safeIndex,
                        totalQuestions = uiState.totalQuestions,
                        question = uiState.questions[safeIndex],
                        selectedAnswer = uiState.selectedAnswer,
                        showExplanation = uiState.showExplanation,
                        onAnswerSelected = viewModel::selectAnswer,
                        onNext = viewModel::nextQuestion
                    )
                }

                uiState.error != null -> {
                    Column(
                        modifier = Modifier.align(Alignment.Center),
                        horizontalAlignment = Alignment.CenterHorizontally
                    ) {
                        Text(uiState.error!!, color = Error)
                        Spacer(modifier = Modifier.height(16.dp))
                        Button(onClick = onBack) {
                            Text("QUAY LẠI")
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun QuizContent(
    currentIndex: Int,
    totalQuestions: Int,
    question: com.knowledgemap.app.domain.model.QuizQuestion,
    selectedAnswer: Int?,
    showExplanation: Boolean,
    onAnswerSelected: (Int) -> Unit,
    onNext: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
    ) {
        LinearProgressIndicator(
            progress = (currentIndex + 1).toFloat() / totalQuestions,
            modifier = Modifier.fillMaxWidth(),
            color = Primary,
            trackColor = MaterialTheme.colorScheme.surfaceVariant
        )

        Text(
            text = "STEP ${currentIndex + 1} / $totalQuestions",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f),
            modifier = Modifier.padding(top = 8.dp),
            letterSpacing = 1.sp
        )

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = question.question,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(24.dp))

        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            question.options.forEachIndexed { index, option ->
                val isSelected = selectedAnswer == index
                val isCorrect = index == question.correctIndex
                
                val borderColor = when {
                    showExplanation && isCorrect -> Secondary
                    showExplanation && isSelected && !isCorrect -> Error
                    isSelected -> Primary
                    else -> MaterialTheme.colorScheme.outline.copy(alpha = 0.2f)
                }
                
                val backgroundColor = when {
                    showExplanation && isCorrect -> Secondary.copy(alpha = 0.1f)
                    showExplanation && isSelected && !isCorrect -> Error.copy(alpha = 0.1f)
                    isSelected -> Primary.copy(alpha = 0.1f)
                    else -> MaterialTheme.colorScheme.surfaceVariant
                }

                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable(enabled = !showExplanation) { onAnswerSelected(index) }
                        .border(1.dp, borderColor, MaterialTheme.shapes.medium),
                    shape = MaterialTheme.shapes.medium,
                    color = backgroundColor
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "${('A' + index)}. ",
                            fontWeight = FontWeight.Bold,
                            color = if (isSelected || (showExplanation && isCorrect)) Color.Unspecified else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                        )
                        Text(text = option, modifier = Modifier.weight(1f))

                        if (showExplanation && isCorrect) {
                            Icon(Icons.Default.Check, null, tint = Secondary)
                        }
                        if (showExplanation && isSelected && !isCorrect) {
                            Icon(Icons.Default.Close, null, tint = Error)
                        }
                    }
                }
            }
        }

        if (showExplanation) {
            Spacer(modifier = Modifier.height(16.dp))
            Surface(
                modifier = Modifier
                    .fillMaxWidth()
                    .border(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.1f), MaterialTheme.shapes.medium),
                shape = MaterialTheme.shapes.medium,
                color = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        "ANALYSIS", 
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f),
                        letterSpacing = 1.sp
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(question.explanation, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))

        Button(
            onClick = onNext,
            modifier = Modifier.fillMaxWidth(),
            enabled = selectedAnswer != null || showExplanation,
            shape = MaterialTheme.shapes.medium
        ) {
            Text(
                if (!showExplanation) "VERIFY" 
                else if (currentIndex < totalQuestions - 1) "NEXT STEP" 
                else "FINALIZE"
            )
        }
    }
}

@Composable
private fun ResultsContent(
    score: Int,
    total: Int,
    skillBefore: Int,
    skillAfter: Int,
    answers: Map<Int, Int>,
    questions: List<com.knowledgemap.app.domain.model.QuizQuestion>,
    onComplete: () -> Unit
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(24.dp)
            .verticalScroll(rememberScrollState()),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Text(
            text = "ASSESSMENT RESULTS",
            style = MaterialTheme.typography.labelSmall,
            color = Primary,
            letterSpacing = 2.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "$score / $total",
            style = MaterialTheme.typography.displayMedium,
            fontWeight = FontWeight.Bold,
            color = if (score.toFloat() / total >= 0.7f) Secondary else Error
        )

        Text(
            text = "SYNC STATUS: ${getSkillLevelColor(skillAfter).let { "COMPLETE" }}",
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
        )

        Spacer(modifier = Modifier.height(32.dp))

        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.2f), MaterialTheme.shapes.medium),
            shape = MaterialTheme.shapes.medium,
            color = MaterialTheme.colorScheme.surfaceVariant
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                questions.forEachIndexed { index, q ->
                    val isCorrect = answers[index] == q.correctIndex
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 8.dp),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            "STEP ${index + 1}", 
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                        )
                        Text(
                            if (isCorrect) "PASSED" else "FAILED",
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = if (isCorrect) Secondary else Error
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = onComplete, 
            modifier = Modifier.fillMaxWidth(),
            shape = MaterialTheme.shapes.medium
        ) {
            Text("RETURN TO CONSTELLATION")
        }
    }
}