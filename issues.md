# UI Logic & Button Issues - STATUS: REVIEW COMPLETE

## 🏠 HomeScreen

| Element | Location | Status | Notes |
|---------|----------|--------|-------|
| Notifications icon | line 41 | ✅ STUBBED | Shows Snackbar "Chức năng đang được phát triển" |
| Recommendation card click | line 82 | ⚠️ BROKEN | `onTopicClick` param default `{}` in NavGraph — never wired to navigation |
| Activity card click | line 101 | ⚠️ BROKEN | `HomeActivityCard` has no `onClick` — no navigation handler |
| Back gesture | — | ⚠️ NOT TRACKED | No custom back handling |

**HomeViewModel issues:**
- Line 60: `masteryPercent` uses `inProgress * 0.5` weight (acceptable heuristic)
- Line 76: `topicNodeDao.getById` can return null — no fallback for null `name` display
- No `refresh()` or `pull-to-refresh` support

---

## 🗺️ KnowledgeMapScreen

| Element | Location | Status | Notes |
|---------|----------|--------|-------|
| Search icon | line 105 | ✅ STUBBED | Shows Snackbar "Tìm kiếm: Chức năng đang được phát triển" |
| Node click | line 200 | ✅ OK | `onTopicClick(topic.id)` → `NavGraph` → Assessment screen |
| EmberListItem click | line 324 | ✅ OK | Same as above |
| Zoom + button | line 217 | ✅ OK | Direct scale manipulation |
| Zoom - button | line 220 | ✅ OK | Direct scale manipulation |
| Center button | line 223 | ✅ OK | Reset scale=1, offset=0 |
| Filter chips | line 240-251 | ✅ OK | `selectedFilter` state, filters `uiState.topics` |
| Recommendations icon | line 294 | ✅ OK | Haptic feedback + `onRecommendationsClick` → Recommendation screen |
| Graph nodes | line 169 | ⚠️ DEMO | Only shows `uiState.topics.take(6)` with dummy hardcoded positions |

**KnowledgeMapViewModel issues:**
- Line 52: `lockedTopicIds` calculated but never used (filter applied but no lock UI)
- Line 49: `completed` = `skillLevel >= 2` but `HomeViewModel` uses `>= 3` — **inconsistent mastery threshold**
- No error state handling
- No loading state

---

## ✅ AssessmentScreen

| Element | Location | Status | Notes |
|---------|----------|--------|-------|
| Back button | NavGraph line 123 | ✅ OK | `popBackStack()` |
| Answer option click | line 206 | ✅ OK | `onAnswerSelected(index)` + haptic, disabled after selection |
| Hint button | line 282 | ✅ OK | Toggle `showHint` state |
| Confirm/Next button | line 297 | ✅ OK | `onNext()` — disabled until answer selected |
| Button color change | line 308 | ✅ OK | Green (correct) / Red (wrong) based on explanation shown |
| Back on error | line 111 | ✅ OK | `onBack()` |
| Result complete button | line 401 | ✅ OK | `onComplete` → pop to home |

**AssessmentViewModel issues:**
- Line 66: `if (selectedAnswer != null) return` — prevents changing answer (correct UX)
- Line 80: `answers + (currentIndex to (selectedAnswer ?: -1))` — uses `-1` sentinel for unanswered, but checked with `>= 0` on line 85
- Line 46: `result.fold` pattern correct
- No timeout handling for quiz generation
- Session stored as nullable `var` — mutation pattern okay for ViewModel-scoped session

---

## 📋 RecommendationScreen (Tasks Tab)

| Element | Location | Status | Notes |
|---------|----------|--------|-------|
| Back button | NavGraph | ✅ OK | `popBackStack()` |
| Start Assessment button | line 147 | ✅ OK | `onTopicClick(rec.topic.id)` → Assessment |
| Retry on error | line 54 | ✅ OK | `viewModel.retry()` → `loadRecommendations()` |
| Retry on empty | line 57 | ✅ OK | Same |
| Refresh button (empty) | line 209 | ✅ OK | `onRetry()` |

**RecommendationViewModel issues:**
- No deduplication — same recommendations shown on every load
- `getTopRecommendations(3)` — hardcoded limit

---

## ⚠️ CROSS-CUTTING ISSUES

1. **Inconsistent mastery threshold**: `KnowledgeMapViewModel` uses `skillLevel >= 2` for "completed", `HomeViewModel` uses `>= 3`. Confusing for users.
2. **Navigation wiring gap**: `HomeScreen` has `onTopicClick` param default `{}` — NavGraph passes nothing (no `onTopicClick` passed). Home recommendations never navigate anywhere.
3. **No loading state**: `KnowledgeMapViewModel`, `RecommendationViewModel` don't show shimmer/skeleton.
4. **Graph is demo-only**: `KnowledgeMapScreen` line 169 uses `take(6)` + hardcoded offsets, not real graph layout.
5. **Locked topics**: `lockedTopicIds` computed but never rendered differently.

---

## 🔧 RECOMMENDED FIXES (Priority Order)

1. **[CRITICAL]** Wire `HomeScreen` → `onTopicClick` in NavGraph
2. **[HIGH]** Unify mastery threshold (use `>= 3` everywhere, or document the difference)
3. **[MEDIUM]** Add shimmer loading states to KnowledgeMap and Recommendation
4. **[MEDIUM]** Fix `HomeActivityCard` — no click handler, can't navigate
5. **[LOW]** Implement real graph layout algorithm