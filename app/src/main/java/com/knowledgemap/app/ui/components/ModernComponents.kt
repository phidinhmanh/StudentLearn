package com.knowledgemap.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.blur
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.knowledgemap.app.domain.model.TopicNode
import com.knowledgemap.app.domain.model.TopicStatus
import com.knowledgemap.app.ui.theme.*

@Composable
fun ModernCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    borderColor: Color = MaterialTheme.colorScheme.outline.copy(alpha = 0.2f),
    content: @Composable () -> Unit
) {
    Card(
        modifier = modifier
            .fillMaxWidth()
            .then(if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier)
            .border(1.dp, borderColor, MaterialTheme.shapes.medium),
        shape = MaterialTheme.shapes.medium,
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp)
    ) {
        Column(
            modifier = Modifier
                .padding(16.dp)
        ) {
            content()
        }
    }
}

@Composable
fun ModernTopicCard(
    topic: TopicNode,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    val status = topic.status
    val skillColor = getSkillLevelColor(topic.skillLevel)
    val isLocked = status == TopicStatus.LOCKED

    ModernCard(
        modifier = modifier,
        onClick = if (!isLocked) onClick else null,
        borderColor = if (status == TopicStatus.LEARNING) Tertiary.copy(alpha = 0.5f) else MaterialTheme.colorScheme.outline.copy(alpha = 0.2f)
    ) {
        Row(
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // Node indicator with luminescence if learning
            Box(contentAlignment = Alignment.Center) {
                if (status == TopicStatus.LEARNING) {
                    Box(
                        modifier = Modifier
                            .size(32.dp)
                            .blur(8.dp)
                            .background(Tertiary.copy(alpha = 0.4f), CircleShape)
                    )
                }
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
                            tint = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f),
                            modifier = Modifier.size(16.dp)
                        )
                    } else if (status == TopicStatus.MASTERED) {
                        Icon(
                            imageVector = Icons.Default.Check,
                            contentDescription = null,
                            tint = OnSecondary,
                            modifier = Modifier.size(16.dp)
                        )
                    }
                }
            }

            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = topic.name,
                    style = MaterialTheme.typography.titleSmall,
                    fontWeight = FontWeight.Bold,
                    maxLines = 1,
                    overflow = TextOverflow.Ellipsis,
                    color = if (isLocked) MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f) else MaterialTheme.colorScheme.onSurface
                )
                Text(
                    text = topic.status.label.uppercase(),
                    style = MaterialTheme.typography.labelSmall,
                    color = if (isLocked) MaterialTheme.colorScheme.onSurface.copy(alpha = 0.3f) else skillColor,
                    letterSpacing = 1.sp
                )
            }

            if (!isLocked) {
                Text(
                    text = "DIFF: ${topic.difficulty}",
                    style = MaterialTheme.typography.labelSmall,
                    color = MaterialTheme.colorScheme.onSurface.copy(alpha = 0.5f)
                )
            }
        }
    }
}

@Composable
fun LuminescentNode(
    name: String,
    status: TopicStatus,
    modifier: Modifier = Modifier,
    onClick: () -> Unit = {}
) {
    val color = getSkillLevelColor(status.level)
    val isLocked = status == TopicStatus.LOCKED

    Column(
        modifier = modifier.clickable(onClick = onClick),
        horizontalAlignment = Alignment.CenterHorizontally
    ) {
        Box(contentAlignment = Alignment.Center) {
            // Glow effect
            if (!isLocked && status != TopicStatus.GAP) {
                Box(
                    modifier = Modifier
                        .size(56.dp)
                        .blur(12.dp)
                        .background(color.copy(alpha = 0.3f), CircleShape)
                )
            }
            
            // Inner stroke for "technical" look
            Box(
                modifier = Modifier
                    .size(48.dp)
                    .border(1.dp, color.copy(alpha = 0.5f), CircleShape)
                    .padding(4.dp)
            ) {
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(if (isLocked) Locked else color, CircleShape)
                )
            }
        }
        
        Spacer(modifier = Modifier.height(8.dp))
        
        Text(
            text = name,
            style = MaterialTheme.typography.labelSmall,
            fontWeight = FontWeight.Medium,
            color = if (isLocked) MaterialTheme.colorScheme.onSurface.copy(alpha = 0.4f) else MaterialTheme.colorScheme.onSurface,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis
        )
    }
}

@Composable
fun ModernChip(
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
                if (selected) Primary else MaterialTheme.colorScheme.outline.copy(alpha = 0.3f),
                MaterialTheme.shapes.medium
            ),
        shape = MaterialTheme.shapes.medium,
        color = if (selected) Primary.copy(alpha = 0.1f) else Color.Transparent
    ) {
        Text(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp),
            text = label.uppercase(),
            style = MaterialTheme.typography.labelSmall,
            fontWeight = if (selected) FontWeight.Bold else FontWeight.Normal,
            color = if (selected) Primary else MaterialTheme.colorScheme.onSurface.copy(alpha = 0.6f),
            letterSpacing = 1.sp
        )
    }
}
