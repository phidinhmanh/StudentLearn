package com.knowledgemap.app.ui.theme

import androidx.compose.ui.graphics.Color

// Core Brand Colors (DESIGN.md)
val Primary = Color(0xFFFFC081)
val PrimaryContainer = Color(0xFFFF9800)
val Secondary = Color(0xFF78DC77)
val SecondaryContainer = Color(0xFF00761F)
val Tertiary = Color(0xFFE1CF17)
val TertiaryContainer = Color(0xFFC4B300)
val Error = Color(0xFFFFB4AB)

// Surface & Neutrals (DESIGN.md)
val Background = Color(0xFF10141A)
val Surface = Color(0xFF10141A)
val SurfaceBright = Color(0xFF353940)
val SurfaceContainer = Color(0xFF1C2026)
val OnBackground = Color(0xFFDFE2EB)
val OnSurface = Color(0xFFDFE2EB)
val OnPrimary = Color(0xFF10141A)
val OnSecondary = Color(0xFF10141A)
val OnTertiary = Color(0xFF10141A)
val OnError = Color(0xFF10141A)
val Outline = Color(0xFFA38D7A)

// State Colors
val Mastered = Secondary
val Learning = Tertiary
val Gap = Error
val Locked = Color(0xFF353940)

fun getSkillLevelColor(skillLevel: Int): Color = when (skillLevel) {
    0 -> Locked
    1 -> Gap
    2 -> Learning
    3 -> Mastered
    else -> Locked
}