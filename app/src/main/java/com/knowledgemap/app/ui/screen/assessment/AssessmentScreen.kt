package com.knowledgemap.app.ui.screen.assessment

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Close
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import com.knowledgemap.app.ui.components.EmberTopBar
import com.knowledgemap.app.ui.theme.*

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
            EmberTopBar(
                title = uiState.topicName.ifEmpty { "Bài tập" },
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

                    AnimatedContent(
                        targetState = safeIndex,
                        transitionSpec = {
                            if (targetState > initialState) {
                                slideInHorizontally { it } + fadeIn() togetherWith
                                        slideOutHorizontally { -it } + fadeOut()
                            } else {
                                slideInHorizontally { -it } + fadeIn() togetherWith
                                        slideOutHorizontally { it } + fadeOut()
                            }.using(SizeTransform(clip = false))
                        },
                        label = "quiz_content"
                    ) { index ->
                        QuizContent(
                            currentIndex = index,
                            totalQuestions = uiState.totalQuestions,
                            question = uiState.questions[index],
                            selectedAnswer = uiState.selectedAnswer,
                            showExplanation = uiState.showExplanation,
                            onAnswerSelected = viewModel::selectAnswer,
                            onNext = viewModel::nextQuestion
                        )
                    }
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
    var showHint by remember(question) { mutableStateOf(false) }
    val haptic = LocalHapticFeedback.current

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState())
    ) {
        // Step Indicator with animation
        val progress by animateFloatAsState(
            targetValue = (currentIndex + 1).toFloat() / totalQuestions,
            animationSpec = tween(500, easing = FastOutSlowInEasing),
            label = "progress"
        )

        LinearProgressIndicator(
            progress = { progress },
            modifier = Modifier
                .fillMaxWidth()
                .height(6.dp),
            color = Primary,
            trackColor = SurfaceBright,
            strokeCap = androidx.compose.ui.graphics.StrokeCap.Round
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Câu ${currentIndex + 1}/$totalQuestions",
            style = MaterialTheme.typography.labelSmall,
            color = OnSurface,
            modifier = Modifier.padding(top = 8.dp)
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = question.question,
            style = MaterialTheme.typography.titleMedium,
            fontWeight = FontWeight.Bold,
            color = OnBackground
        )

        Spacer(modifier = Modifier.height(32.dp))

        Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            question.options.forEachIndexed { index, option ->
                val isSelected = selectedAnswer == index
                val isCorrect = index == question.correctIndex

                val borderColor by animateColorAsState(
                    targetValue = when {
                        showExplanation && isCorrect -> Mastered
                        showExplanation && isSelected && !isCorrect -> Error
                        isSelected -> Primary
                        else -> Outline
                    },
                    label = "border_color"
                )

                val backgroundColor by animateColorAsState(
                    targetValue = when {
                        showExplanation && isCorrect -> Mastered.copy(alpha = 0.1f)
                        showExplanation && isSelected && !isCorrect -> Error.copy(alpha = 0.1f)
                        isSelected -> Primary.copy(alpha = 0.1f)
                        else -> Surface
                    },
                    label = "bg_color"
                )

                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .animateContentSize()
                        .clickable(enabled = !showExplanation) {
                            haptic.performHapticFeedback(HapticFeedbackType.TextHandleMove)
                            onAnswerSelected(index)
                        }
                        .border(1.dp, borderColor, MaterialTheme.shapes.small),
                    shape = MaterialTheme.shapes.small,
                    color = backgroundColor
                ) {
                    Row(
                        modifier = Modifier.padding(16.dp),
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Text(
                            text = "${('A' + index)}. ",
                            fontWeight = FontWeight.Bold,
                            color = if (isSelected || (showExplanation && isCorrect)) OnBackground else OnSurface
                        )
                        Text(text = option, modifier = Modifier.weight(1f), color = OnBackground)

                        AnimatedVisibility(
                            visible = showExplanation && (isCorrect || (isSelected && !isCorrect)),
                            enter = scaleIn(spring(Spring.DampingRatioMediumBouncy)) + fadeIn(),
                            exit = scaleOut() + fadeOut()
                        ) {
                            Icon(
                                imageVector = if (isCorrect) Icons.Default.Check else Icons.Default.Close,
                                contentDescription = null,
                                tint = if (isCorrect) Mastered else Error,
                                modifier = Modifier.size(24.dp)
                            )
                        }
                    }
                }
            }
        }

        AnimatedVisibility(
            visible = showExplanation || showHint,
            enter = slideInVertically { it / 2 } + fadeIn(tween(delayMillis = 200)),
            exit = slideOutVertically { it / 2 } + fadeOut()
        ) {
            Column {
                Spacer(modifier = Modifier.height(24.dp))
                Surface(
                    modifier = Modifier
                        .fillMaxWidth()
                        .border(1.dp, Outline, MaterialTheme.shapes.small),
                    shape = MaterialTheme.shapes.small,
                    color = SurfaceBright
                ) {
                    Column(modifier = Modifier.padding(16.dp)) {
                        Text(
                            if (showExplanation) "Giải thích" else "Gợi ý từ AI",
                            style = MaterialTheme.typography.labelSmall,
                            color = OnSurface
                        )
                        Spacer(modifier = Modifier.height(8.dp))
                        Text(
                            if (showExplanation) question.explanation else "Hãy xem lại kiến thức về ${question.question.substringBefore(" ")}",
                            style = MaterialTheme.typography.bodyMedium,
                            color = OnBackground
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.weight(1f))
        Spacer(modifier = Modifier.height(24.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            var showHint by remember { mutableStateOf(false) }

            OutlinedButton(
                onClick = { showHint = !showHint },
                modifier = Modifier.weight(1f),
                shape = MaterialTheme.shapes.small,
                colors = ButtonDefaults.outlinedButtonColors(contentColor = Primary)
            ) {
                Text(if (showHint) "Ẩn gợi ý" else "Gợi ý")
            }

            var isPressed by remember { mutableStateOf(false) }
            val buttonScale by animateFloatAsState(
                targetValue = if (isPressed) 0.92f else 1f,
                label = "btn_scale"
            )

            Button(
                onClick = {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onNext()
                },
                modifier = Modifier
                    .weight(1f)
                    .scale(buttonScale),
                enabled = selectedAnswer != null || showExplanation,
                shape = MaterialTheme.shapes.small,
                colors = ButtonDefaults.buttonColors(
                    containerColor = if (showExplanation) {
                        if (selectedAnswer == question.correctIndex) Mastered else Error
                    } else Primary,
                    contentColor = OnPrimary
                )
            ) {
                Text(
                    if (!showExplanation) "Xác nhận"
                    else if (currentIndex < totalQuestions - 1) "Câu tiếp theo"
                    else "Hoàn thành"
                )
            }
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
            text = "KẾT QUẢ BÀI TẬP",
            style = MaterialTheme.typography.labelSmall,
            color = Primary,
            letterSpacing = 2.sp
        )

        Spacer(modifier = Modifier.height(16.dp))

        val scorePercentage = score.toFloat() / total
        Text(
            text = "$score / $total",
            style = MaterialTheme.typography.headlineLarge,
            color = if (scorePercentage >= 0.7f) Mastered else Error
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "Kỹ năng: L$skillBefore → L$skillAfter",
            style = MaterialTheme.typography.bodyMedium,
            color = OnSurface
        )

        Spacer(modifier = Modifier.height(32.dp))

        Surface(
            modifier = Modifier
                .fillMaxWidth()
                .border(1.dp, Outline, MaterialTheme.shapes.medium),
            shape = MaterialTheme.shapes.medium,
            color = Surface
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
                            "Câu ${index + 1}",
                            style = MaterialTheme.typography.bodyMedium,
                            color = OnBackground
                        )
                        Text(
                            if (isCorrect) "Đúng" else "Sai",
                            style = MaterialTheme.typography.labelMedium,
                            color = if (isCorrect) Mastered else Error
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(32.dp))

        Button(
            onClick = onComplete,
            modifier = Modifier.fillMaxWidth(),
            shape = MaterialTheme.shapes.small,
            colors = ButtonDefaults.buttonColors(containerColor = Primary, contentColor = OnPrimary)
        ) {
            Text("Quay về trang chủ")
        }
    }
}