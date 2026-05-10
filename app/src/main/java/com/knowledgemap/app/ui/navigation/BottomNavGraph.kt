package com.knowledgemap.app.ui.navigation

import androidx.annotation.DrawableRes
import com.knowledgemap.app.R

sealed class BottomBarScreen(
    val route: String,
    val title: String,
    @DrawableRes val iconRes: Int
) {
    data object Home : BottomBarScreen(
        route = "home",
        title = "Trang chủ",
        iconRes = R.drawable.ic_nav_home
    )

    data object Graph : BottomBarScreen(
        route = "graph",
        title = "Sơ đồ",
        iconRes = R.drawable.ic_nav_graph
    )

    data object Quiz : BottomBarScreen(
        route = "quiz",
        title = "Nhiệm vụ",
        iconRes = R.drawable.ic_nav_quiz
    )

    data object Profile : BottomBarScreen(
        route = "profile",
        title = "Cá nhân",
        iconRes = R.drawable.ic_nav_profile
    )
}
