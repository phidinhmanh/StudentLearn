package com.knowledgemap.app.ui.screen.knowledge

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.knowledgemap.app.data.local.dao.TopicNodeDao
import com.knowledgemap.app.domain.model.TopicNode
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class KnowledgeMapUiState(
    val isLoading: Boolean = true,
    val topics: List<TopicNode> = emptyList(),
    val completedCount: Int = 0,
    val totalCount: Int = 0,
    val progressPercent: Int = 0,
    val lockedTopicIds: Set<String> = emptySet()
)

@HiltViewModel
class KnowledgeMapViewModel @Inject constructor(
    private val topicNodeDao: TopicNodeDao
) : ViewModel() {

    private val _uiState = MutableStateFlow(KnowledgeMapUiState())
    val uiState: StateFlow<KnowledgeMapUiState> = _uiState.asStateFlow()

    init {
        loadTopics()
    }

    private fun loadTopics() {
        viewModelScope.launch {
            topicNodeDao.getAllBySubject("toan10").collect { entities ->
                val topics = entities.map { entity ->
                    TopicNode(
                        id = entity.id,
                        name = entity.name,
                        desc = entity.desc,
                        difficulty = entity.difficulty,
                        chapter = entity.chapter,
                        subject = entity.subject,
                        skillLevel = entity.skillLevel,
                        lastAssessed = entity.lastAssessed
                    )
                }
                val completed = topics.count { it.skillLevel >= 3 }
                val inProgress = topics.count { it.skillLevel in 1..2 }
                val total = topics.size
                val percent = if (total > 0) ((completed + inProgress * 0.5) * 100 / total).toInt() else 0
                val lockedIds = topics.filter { it.skillLevel == 0 }.map { it.id }.toSet()

                _uiState.value = KnowledgeMapUiState(
                    isLoading = false,
                    topics = topics,
                    completedCount = completed,
                    totalCount = total,
                    progressPercent = percent,
                    lockedTopicIds = lockedIds
                )
            }
        }
    }
}
