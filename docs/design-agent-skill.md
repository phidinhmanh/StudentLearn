# Design Agent Skill - User-Centered Design (UCD) Methodology

## Agent Overview

**Tên:** Design Agent
**Role:** Nghiên cứu và thiết kế trải nghiệm người dùng
**Phạm vi:** UX Research → UI Design → Usability Testing → Iteration

---

## Phase 1: User Research (Nghiên cứu người dùng)

### 1.1 Thu thập yêu cầu
**Các phương pháp:**
- Phỏng vấn người dùng (Interviews)
- Quan sát thực địa (Field Observation)
- Khảo sát (Surveys)
- Phân tích竞争对手 (Competitive Analysis)

**Output:**
- Báo cáo nghiên cứu người dùng
- Danh sách nhu cầu và pain points

### 1.2 Xây dựng Persona
**Template:**
```markdown
## Persona: [Tên]

### Thông tin cơ bản
- Tuổi: XX
- Nghề nghiệp: [Student/Worker/etc]
- Trình độ công nghệ: [High/Medium/Low]

### Mục tiêu (Goals)
- Mục tiêu chính: ...
- Mục tiêu phụ: ...

### Hành vi (Behaviors)
- Tần suất sử dụng: ...
- Device preference: ...
- Đã dùng apps tương tự: ...

### Rào cản (Pain Points)
- Vấn đề hiện tại: ...
- Frustrations: ...

### Kỳ vọng (Expectations)
- ...
```

### 1.3 User Journey Map
**Format:**
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│   Stage     │   Actions   │  Pain Points│  Opportunities│
├─────────────┼─────────────┼─────────────┼─────────────┤
│ Discovery   │ ...         │ ...         │ ...         │
│ Consideration│ ...        │ ...         │ ...         │
│ Decision    │ ...         │ ...         │ ...         │
│ Onboarding  │ ...         │ ...         │ ...         │
│ Usage       │ ...         │ ...         │ ...         │
│ Retention   │ ...         │ ...         │ ...         │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

---

## Phase 2: Task Analysis (Phân tích nhiệm vụ)

### 2.1 Task Decomposition
**Format:**
```markdown
### Task: [Tên nhiệm vụ]
- **Mục tiêu:** ...
- **Input:** ...
- **Output:** ...
- **Steps:**
  1. ...
  2. ...
- **Success Criteria:**
  - Effectiveness: ...
  - Efficiency: ...
  - Satisfaction: ...
```

### 2.2 Information Architecture
**Deliverable:**
```
[App Name]
├── Home (Dashboard)
├── Knowledge Map
│   ├── Chapter List
│   ├── Topic Grid
│   └── Topic Detail
├── Assessment
│   ├── Quiz Screen
│   ├── Results
│   └── History
├── Recommendation
│   └── Top 3 Suggestions
└── Profile
    ├── Sessions
    └── Settings
```

---

## Phase 3: Conceptual Design (Thiết kế khái niệm)

### 3.1 Interaction Scenarios
**Format:**
```markdown
### Scenario: [Tên]
**Bối cảnh:** [Where/When/Context]
**Người dùng:** [Persona]
**Mục tiêu:** [Goal]

**Luồng tương tác:**
1. User [action]
2. System [response]
3. User [action]
...

**Kết quả:** [Outcome]
```

### 3.2 Wireframe Checklist
- [ ] Navigation flow (điều hướng rõ ràng)
- [ ] Content hierarchy (phân cấp nội dung)
- [ ] Consistency (nhất quán)
- [ ] Feedback mechanisms (cơ chế phản hồi)
- [ ] Error handling (xử lý lỗi)

---

## Phase 4: UI Design & Prototyping

### 4.1 Design System

#### Color Palette
```kotlin
// Primary Colors
val Primary = Color(0xFF1976D2)
val PrimaryVariant = Color(0xFF1565C0)
val OnPrimary = Color(0xFFFFFFFF)

// Skill Level Colors (FR-06)
val SkillLevel0 = Color(0xFF9E9E9E) // Xám - Chưa học
val SkillLevel1 = Color(0xFFF44336) // Đỏ - Cần ôn
val SkillLevel2 = Color(0xFFFFC107) // Vàng - Đang học
val SkillLevel3 = Color(0xFF4CAF50) // Xanh - Đã vững

// States
val Error = Color(0xFFB00020)
val Success = Color(0xFF4CAF50)
val Warning = Color(0xFFFFC107)
```

#### Typography Scale
```kotlin
// Material 3 Typography
HeadlineLarge: 32sp
HeadlineMedium: 28sp
TitleLarge: 22sp
TitleMedium: 16sp
BodyLarge: 16sp
BodyMedium: 14sp
LabelLarge: 14sp
LabelMedium: 12sp
```

#### Spacing System (8pt Grid)
```kotlin
val Space2 = 2.dp
val Space4 = 4.dp
val Space8 = 8.dp
val Space16 = 16.dp
val Space24 = 24.dp
val Space32 = 32.dp
val Space48 = 48.dp
```

#### Component Patterns
```markdown
### Topic Card
- Size: 160x120dp
- Border radius: 12dp
- Shadow: elevation 4dp
- Content: Icon + Name + Skill indicator
- States: Default, Selected, Locked (grayed + lock icon)

### Quiz Question
- Question text: TitleMedium, left-aligned
- Options: Card vertical stack, 8dp gap
- Option: BodyMedium, padding 16dp, border radius 8dp
- States: Default, Selected, Correct (green), Wrong (red)
```

### 4.2 Screen Specifications

#### Screen 1: Knowledge Map (FR-05, FR-06, FR-07)
```
┌─────────────────────────────────────┐
│ [AppBar: Knowledge Map - Toán 10]    │
├─────────────────────────────────────┤
│ Filter: [Tất cả ▼] [Cần ôn] [Chưa]  │
├─────────────────────────────────────┤
│ Chương 1: Mệnh đề - Tập hợp         │
│ ┌────┐ ┌────┐ ┌────┐ ┌────┐        │
│ │ 🔓 │ │ 🔒 │ │ 🔓 │ │ 🔓 │        │
│ │L2  │ │L0🔒│ │L1  │ │L0  │        │
│ └────┘ └────┘ └────┘ └────┘        │
│                                     │
│ Chương 2: Hàm số bậc nhất & bậc hai │
│ ┌────┐ ┌────┐ ┌────┐               │
│ │ 🔒 │ │ 🔒 │ │ 🔒 │               │
│ └────┘ └────┘ └────┘               │
├─────────────────────────────────────┤
│ [Progress: 25% hoàn thành]          │
├─────────────────────────────────────┤
│ [Recommendation: Top 3 suggestion]   │
└─────────────────────────────────────┘

Legend:
🔓 = Unlocked (prereq >= 2)
🔒 = Locked (prereq < 2)
L0 = Skill Level 0 (gray)
L1 = Skill Level 1 (red)
L2 = Skill Level 2 (yellow)
L3 = Skill Level 3 (green)
```

#### Screen 2: Assessment Quiz (FR-15, FR-16)
```
┌─────────────────────────────────────┐
│ [AppBar: ← Topic Name] [1/5]        │
├─────────────────────────────────────┤
│                                     │
│ Câu 1: [Question text]              │
│                                     │
│ ┌─────────────────────────────┐    │
│ │ A. [Option A]               │ ← correct=green
│ └─────────────────────────────┘    │
│ ┌─────────────────────────────┐    │
│ │ B. [Option B]               │ ← selected=wrong
│ └─────────────────────────────┘    │
│ ┌─────────────────────────────┐    │
│ │ C. [Option C]               │    │
│ └─────────────────────────────┘    │
│ ┌─────────────────────────────┐    │
│ │ D. [Option D]               │    │
│ └─────────────────────────────┘    │
│                                     │
├─────────────────────────────────────┤
│ [Explanation panel - appears after] │
│ ✅ Giải thích: ...                   │
└─────────────────────────────────────┘
```

#### Screen 3: Recommendation (FR-19, FR-20)
```
┌─────────────────────────────────────┐
│ [AppBar: Gợi ý học tập]             │
├─────────────────────────────────────┤
│                                     │
│ Top 1 (Ưu tiên cao nhất)            │
│ ┌─────────────────────────────┐    │
│ │ 📚 Phương trình bậc nhất    │    │
│ │ Lý do: Tiền đề của Bất      │    │
│ │ phương trình sắp học        │    │
│ │ [Bắt đầu Kiểm tra →]        │    │
│ └─────────────────────────────┘    │
│                                     │
│ Top 2                               │
│ ┌─────────────────────────────┐    │
│ │ 📚 Hàm số bậc hai           │    │
│ │ Lý do: Đã đủ điều kiện     │    │
│ │ [Bắt đầu Kiểm tra →]        │    │
│ └─────────────────────────────┘    │
│                                     │
│ Top 3                               │
│ ┌─────────────────────────────┐    │
│ │ 📚 Đồ thị hàm số            │    │
│ │ Lý do: Chưa ôn 15 ngày      │    │
│ │ [Bắt đầu Kiểm tra →]        │    │
│ └─────────────────────────────┘    │
└─────────────────────────────────────┘
```

### 4.3 Prototype Workflow

```
[Paper Sketch] → [Low-fi Wireframe] → [Hi-fi Mockup] → [Interactive Prototype]
     ↓               ↓                    ↓                ↓
 10 min           2-4 hours           1-2 days          3-5 days
```

---

## Phase 5: Evaluation & Testing

### 5.1 Heuristic Evaluation Checklist

| # | Heuristic | Description | Severity |
|---|-----------|-------------|----------|
| 1 | Visibility of system status | Feedback, progress indicators | High |
| 2 | Match between system and real world | Icons, terminology familiar | High |
| 3 | User control and freedom | Back button, undo, cancel | High |
| 4 | Consistency and standards | Same patterns across app | Medium |
| 5 | Error prevention | Confirmation dialogs, constraints | High |
| 6 | Recognition rather than recall | Show options, don't hide | Medium |
| 7 | Flexibility and efficiency of use | Shortcuts for experts | Low |
| 8 | Aesthetic and minimalist design | Clean, focused UI | Low |
| 9 | Help users recognize and recover errors | Clear error messages | High |
| 10 | Help and documentation | In-app help, tutorials | Low |

### 5.2 Usability Test Plan

```markdown
## Usability Test: [Feature Name]

### Objectives
1. [Objective 1]
2. [Objective 2]

### Tasks
| # | Task | Success Criteria | Time Limit |
|---|------|------------------|------------|
| 1 | [Task description] | [What counts as success] | [X min] |
| 2 | [Task description] | [What counts as success] | [X min] |

### Metrics
- Task Completion Rate: Target ≥ 90%
- Time on Task: Target ≤ [X] seconds
- Error Rate: Target ≤ 10%
- SUS Score: Target ≥ 70

### Participants
- Number: 5-10 users
- Profile: Target persona matching
- Recruitment: [Method]
```

### 5.3 Iteration Loop

```
┌───────────────┐
│ Design Phase  │
│ (Phase 1-4)   │
└───────┬───────┘
        ↓
┌───────────────┐
│   Testing     │
│ (Phase 5)     │
└───────┬───────┘
        ↓
    ┌───┴───┐
    ↓       ↓
 [Pass?]  [Fail?]
    ↓       ↓
   END    Back to
          Design
```

---

## Phase 6: Build & Release

### 6.1 Design Handoff Checklist

**UI Specification Document:**
- [ ] Color palette (hex codes)
- [ ] Typography (font family, sizes, weights)
- [ ] Spacing system (8pt grid)
- [ ] Component library (buttons, cards, inputs)
- [ ] Icon set (size, style)
- [ ] Animation specs (durations, easing)
- [ ] Screen flows (navigation map)

**Asset Requirements:**
- [ ] App icon (multiple sizes)
- [ ] Illustrations (onboarding, empty states)
- [ ] Icon set (Material Icons recommended)
- [ ] Splash screen
- [ ] Error/Success illustrations

### 6.2 Quality Gates

**Before Code Review:**
- [ ] All screens designed
- [ ] All states covered (default, hover, active, error, loading)
- [ ] Dark mode support (if required)
- [ ] Accessibility compliance (WCAG 2.1 AA)

**Before Release:**
- [ ] Usability test passed
- [ ] Performance benchmarks met
- [ ] Accessibility audit complete

---

## Design Agent Output Templates

### Template 1: Design Brief
```markdown
# Design Brief: [Feature Name]

## 1. Overview
**Feature:** ...
**User Goal:** ...
**Business Value:** ...

## 2. User Research
**Persona:** ...
**Pain Points:** ...
**Opportunities:** ...

## 3. Requirements
**Must Have:**
- ...
**Should Have:**
- ...
**Nice to Have:**
- ...

## 4. Design Solution
**Approach:** ...
**Screens:** ...
**Interactions:** ...

## 5. Metrics
**Success Metrics:**
- ...
**Measurement Method:**
- ...
```

### Template 2: Design Spec
```markdown
# Design Spec: [Screen Name]

## Layout
[Description of layout structure]

## Components
| Component | Description | States |
|-----------|-------------|--------|
| ... | ... | ... |

## Interactions
| Action | Result |
|--------|--------|
| ... | ... |

## States
| State | Visual |
|-------|--------|
| Default | ... |
| Loading | ... |
| Error | ... |
| Empty | ... |

## Accessibility
- Screen reader support: ...
- Touch target size: ...
- Color contrast: ...
```

---

## Dependencies with Other Agents

| Design Output | Consumed By |
|---------------|-------------|
| Screen specs → wireframes | UI Agent (Agent 7) |
| Component library | UI Agent |
| Interaction patterns | UI Agent, Assessment Agent |
| User research data | Recommendation Agent |
| Persona profiles | All Agents |

---

## Key Constraints for Design

- **NFR-09:** Onboarding ≤ 3 phút hoàn thành
- **NFR-05:** Offline mode hoạt động (design for both states)
- **FR-06:** Skill level color coding (accessibility compliant)
- **CON-S03:** INTERNET permission only (no camera/mic)
- **Mobile-first:** Touch targets ≥ 48dp