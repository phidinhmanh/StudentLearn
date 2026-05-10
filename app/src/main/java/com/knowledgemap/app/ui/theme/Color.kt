package com.knowledgemap.app.ui.theme

import androidx.compose.ui.graphics.Color

// ── Ember Dark-Space Palette ──

// Background & Surface
val Background = Color(0xFF0B0B0E)
val Surface = Color(0xFF1C1C1E)
val SurfaceBright = Color(0xFF2A2A2E)
val SurfaceContainer = Color(0xFF1C1C1E)

// Primary – Cam rực lửa
val Primary = Color(0xFFF57C00)
val PrimaryContainer = Color(0xFFFF8C00)
val OnPrimary = Color(0xFFFFFFFF)

// Secondary – Vàng nhạt (XP / Level progress)
val Secondary = Color(0xFFFFC107)
val SecondaryContainer = Color(0xFFFFD54F)
val OnSecondary = Color(0xFF0B0B0E)

// Tertiary – Tím xanh (icon chủ đạo)
val Tertiary = Color(0xFF3F51B5)
val TertiaryContainer = Color(0xFF5C6BC0)
val OnTertiary = Color(0xFFFFFFFF)

// Error
val Error = Color(0xFFFF3D00)
val OnError = Color(0xFFFFFFFF)

// Text on surfaces
val OnBackground = Color(0xFFF5F5F5)
val OnSurface = Color(0xFFB0B0B0)

// Outline / Border
val Outline = Color(0xFF4A4A4A)

// Disabled
val Disabled = Color(0xFF4A4A4A)

// ── State Colors (Knowledge Graph) ──
val Mastered = Color(0xFF4CAF50)   // Xanh lá
val Learning = Color(0xFFFFC107)   // Vàng
val Gap = Color(0xFFFF3D00)        // Đỏ
val Locked = Color(0xFF4A4A4A)     // Xám

fun getSkillLevelColor(skillLevel: Int): Color = when (skillLevel) {
    0 -> Locked
    1 -> Gap
    2 -> Learning
    3 -> Mastered
    else -> Locked
}
