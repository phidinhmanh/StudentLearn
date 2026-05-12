# UI Logic & Button Issues - STATUS: MOSTLY FIXED

## 🏠 HomeScreen
- `IconButton` (line 38): Notifications button has empty `onClick` listener. (PENDING: Needs notification system)
- `masteryPercent`: Calculation in `HomeViewModel` (line 60) uses hardcoded `0.5` weight for in-progress topics.

## 🚀 OnboardingScreen
- `Button` (line 201): FIXED - Added `animateScrollToPage` logic.
- `OnboardingViewModel` (line 63): FIXED - Switched to `hiltViewModel()`.

## 📝 AssessmentScreen
- `OutlinedButton` (line 276): FIXED - Implemented AI hint display.
- `onComplete` (line 124): Quay về trang chủ.

## 🗺️ KnowledgeMapScreen
- `IconButton` (line 93): Search button empty. (PENDING: Needs search feature)
- `KnowledgeNode` (line 187): FIXED - Removed 150ms delay.
- `onRecommendationsClick` (line 285): FIXED - Added haptic feedback.

## 👤 ProfileScreen
- `IconButton` (line 50): Settings button empty.
- `showFileMenu` (line 32): FIXED - Added `DropdownMenu` with Rename/Delete stubs.

## ⏱️ SessionLoggerScreen
- `ViewModel` (line 49): FIXED - Added `LaunchedEffect` to call `loadTopic`.
- `onComplete` (line 132): FIXED - Now waits for VM to finish saving before navigating.
