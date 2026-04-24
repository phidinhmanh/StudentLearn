# API Contracts - KnowledgeMap Learning App

## 1. Gemini API Contracts

### 1.1 Quiz Generation Request (Assessment)

**Endpoint:** `POST https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent`

**Request Body:**
```json
{
  "contents": [{
    "parts": [{
      "text": "<prompt>"
    }]
  }],
  "generationConfig": {
    "temperature": 0.7,
    "maxOutputTokens": 2048,
    "topP": 0.9
  }
}
```

**Prompt Template (FR-11, CON-A02):**
```
Bạn là giáo viên Toán lớp 10. Tạo 5 câu trắc nghiệm về topic: {topic_name}

Context từ Knowledge Graph:
{prerequisite_topics}

Skill Level hiện tại của user: {skill_level} (0=Chưa học, 1=Cần ôn, 2=Đang học, 3=Đã vững)

Yêu cầu:
- Mỗi câu có 4 đáp án (A, B, C, D)
- Độ khó phù hợp với skill level
- Trả lời JSON array theo format sau:

[
  {
    "q": "Câu hỏi",
    "opts": ["Đáp án A", "Đáp án B", "Đáp án C", "Đáp án D"],
    "correct": 0,
    "explain": "Giải thích đáp án đúng"
  },
  ...
]
```

### 1.2 Quiz Generation Response

**Expected Response (valid JSON):**
```json
[
  {
    "q": "Phương trình bậc nhất một ẩn có dạng:",
    "opts": [
      "ax + b = 0",
      "ax² + bx + c = 0",
      "ax + by + c = 0",
      "x² + x + 1 = 0"
    ],
    "correct": 0,
    "explain": "Phương trình bậc nhất một ẩn luôn có dạng ax + b = 0 với a ≠ 0"
  },
  {
    "q": "...",
    "opts": [...],
    "correct": 1,
    "explain": "..."
  }
]
```

**Validation (CON-A05):**
- Mỗi object phải có đủ 4 fields: `q`, `opts`, `correct`, `explain`
- `opts` phải là array 4 phần tử
- `correct` phải ∈ {0, 1, 2, 3}
- Thiếu field → bỏ câu đó, không crash

---

### 1.3 Knowledge Graph Extraction Request (Ingestion)

**Prompt Template:**
```
Phân tích văn bản sau và trích xuất Knowledge Graph về Toán lớp 10:

{chunked_text}

Trả lời JSON array các topic nodes:

[
  {
    "id": "topic_unique_id",
    "name": "Tên topic (tiếng Việt)",
    "desc": "Mô tả ngắn (≤100 ký tự)",
    "difficulty": 1,
    "prereq": ["id_topic_cần_học_trước"]
  }
]

Các loại quan hệ:
- prerequisite: Phải học trước (A prerequisite của B = A → B)
- sequenceOf: Cùng chương, thứ tự
- relatedTo: Liên quan

Chỉ trả JSON, không giải thích.
```

**Response:**
```json
[
  {
    "id": "pt_bac_nhat",
    "name": "Phương trình bậc nhất một ẩn",
    "desc": "Dạng ax + b = 0, cách giải và biện luận",
    "difficulty": 1,
    "prereq": []
  },
  {
    "id": "pt_bac_hai",
    "name": "Phương trình bậc hai một ẩn",
    "desc": "Dạng ax² + bx + c = 0, công thức nghiệm",
    "difficulty": 2,
    "prereq": ["pt_bac_nhat"]
  }
]
```

---

## 2. Room Database Contracts

### 2.1 TopicNode Table

```sql
CREATE TABLE topic_node (
    id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    desc TEXT NOT NULL,
    difficulty INTEGER NOT NULL CHECK (difficulty IN (1, 2, 3)),
    chapter TEXT NOT NULL,
    subject TEXT NOT NULL DEFAULT 'toan10',
    skill_level INTEGER NOT NULL DEFAULT 0 CHECK (skill_level IN (0, 1, 2, 3)),
    last_assessed INTEGER
);
```

**Constraints (CON-D02):**
- `id`: Unique identifier
- `skill_level`: Chỉ nhận giá trị {0, 1, 2, 3}
- `difficulty`: Chỉ nhận giá trị {1, 2, 3}

### 2.2 TopicEdge Table

```sql
CREATE TABLE topic_edge (
    from_id TEXT NOT NULL REFERENCES topic_node(id),
    to_id TEXT NOT NULL REFERENCES topic_node(id),
    relation TEXT NOT NULL CHECK (relation IN ('prerequisite', 'sequenceOf', 'relatedTo')),
    weight REAL DEFAULT 1.0 CHECK (weight > 0),
    PRIMARY KEY (from_id, to_id, relation)
);
```

**Constraints (CON-D01):**
- Directed edge với labels
- `prerequisite`: A → B nghĩa là phải học A trước B
- `sequenceOf`: Cùng chương, thứ tự học
- `relatedTo`: Liên quan nhưng không bắt buộc

### 2.3 AssessmentHistory Table

```sql
CREATE TABLE assessment_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id TEXT NOT NULL REFERENCES topic_node(id),
    score INTEGER NOT NULL CHECK (score >= 0 AND score <= 5),
    skill_before INTEGER NOT NULL CHECK (skill_before IN (0, 1, 2, 3)),
    skill_after INTEGER NOT NULL CHECK (skill_after IN (0, 1, 2, 3)),
    timestamp INTEGER NOT NULL,
    source TEXT NOT NULL CHECK (source IN ('gemini', 'self_report'))
);
```

### 2.4 SessionLog Table

```sql
CREATE TABLE session_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id TEXT NOT NULL REFERENCES topic_node(id),
    started_at INTEGER NOT NULL,
    ended_at INTEGER,
    self_rating INTEGER CHECK (self_rating IN (0, 1, 2))
);
```

**Self Rating Values:**
- 0: Chưa hiểu
- 1: Cần ôn lại
- 2: Hiểu rõ

---

## 3. Domain Models

### 3.1 TopicNode (Domain Model)

```kotlin
data class TopicNode(
    val id: String,
    val name: String,
    val desc: String,
    val difficulty: Int, // 1, 2, 3
    val chapter: String,
    val subject: String = "toan10",
    val skillLevel: Int, // 0, 1, 2, 3
    val lastAssessed: Long? = null
)
```

### 3.2 TopicEdge (Domain Model)

```kotlin
data class TopicEdge(
    val fromId: String,
    val toId: String,
    val relation: EdgeRelation,
    val weight: Float = 1.0f
)

enum class EdgeRelation {
    PREREQUISITE,
    SEQUENCE_OF,
    RELATED_TO
}
```

### 3.3 QuizQuestion (Domain Model)

```kotlin
data class QuizQuestion(
    val question: String,
    val options: List<String>, // 4 options
    val correctIndex: Int, // 0-3
    val explanation: String
)
```

### 3.4 Recommendation (Domain Model)

```kotlin
data class Recommendation(
    val topic: TopicNode,
    val reason: String, // e.g., "Kết quả yếu lần trước"
    val priority: Int // Lower = higher priority
)
```

---

## 4. Skill Level Calculation (FR-13)

```kotlin
fun calculateSkillLevel(correctAnswers: Int): Int {
    return when (correctAnswers) {
        in 0..1 -> 1 // Cần ôn
        in 2..3 -> 2 // Đang học
        in 4..5 -> 3 // Đã vững
        else -> 0
    }
}
```

**Self-Rating Mapping (FR-22):**
```kotlin
fun applySelfRating(currentLevel: Int, rating: SelfRating): Int {
    return when (rating) {
        SelfRating.HIEU_RO -> minOf(currentLevel + 1, 3)
        SelfRating.CAN_ON -> currentLevel
        SelfRating.CHUA_HIEU -> maxOf(currentLevel - 1, 0)
    }
}
```

**Conflict Resolution (FR-23):**
- Khi AI assessment và self-report mâu thuẫn
- Ưu tiên giá trị THẤP HƠN → tránh overconfidence

---

## 5. Recommendation Priority Algorithm (FR-17)

```kotlin
fun calculatePriority(topic: TopicNode, allTopics: List<TopicNode>): Int {
    // Priority 1: Skill Level 1 là prerequisite của topic sắp học
    if (topic.skillLevel == 1 && isPrerequisiteOfInProgressTopic(topic)) {
        return 1
    }
    // Priority 2: Skill Level 0 đã đủ prerequisite
    if (topic.skillLevel == 0 && areAllPrerequisitesMet(topic)) {
        return 2
    }
    // Priority 3: Skill Level 2 chưa ôn lâu nhất
    if (topic.skillLevel == 2) {
        return 3 + daysSinceLastAssessed(topic)
    }
    return 100 // Low priority
}
```

---

## 6. Error Handling

### 6.1 API Timeout (CON-A01)
```json
{
  "error": "API_TIMEOUT",
  "message": "Không thể phân tích tài liệu. Kiểm tra kết nối và thử lại.",
  "retryable": true
}
```

### 6.2 JSON Parse Error (CON-A05)
```json
{
  "error": "PARSE_ERROR",
  "message": "Dữ liệu không hợp lệ. Bỏ qua câu bị lỗi.",
  "validQuestions": [...]
}
```

---

## 7. JSON Asset Schema (CON-D05, CON-G04)

### Default Graph: `assets/toan10_graph.json`

```json
{
  "version": "1.0",
  "subject": "toan10",
  "chapters": [
    {
      "id": "chuong_1",
      "name": "Mệnh đề - Tập hợp",
      "topics": [
        {
          "id": "menh_de",
          "name": "Mệnh đề",
          "desc": "Khái niệm mệnh đề, mệnh đề chứa biến",
          "difficulty": 1,
          "prereq": []
        }
      ]
    }
  ],
  "edges": [
    {
      "from": "pt_bac_nhat",
      "to": "pt_bac_hai",
      "relation": "prerequisite",
      "weight": 1.0
    }
  ]
}
```
