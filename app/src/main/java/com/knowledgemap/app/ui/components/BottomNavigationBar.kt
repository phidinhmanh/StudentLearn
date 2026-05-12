package com.knowledgemap.app.ui.components

import androidx.compose.ui.platform.testTag
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.size
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.ColorFilter
import androidx.compose.ui.res.painterResource
import androidx.compose.ui.unit.dp
import androidx.navigation.NavDestination
import androidx.navigation.NavDestination.Companion.hierarchy
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavHostController
import androidx.navigation.compose.currentBackStackEntryAsState
import com.knowledgemap.app.ui.navigation.BottomBarScreen
import com.knowledgemap.app.ui.theme.Background
import com.knowledgemap.app.ui.theme.Error
import com.knowledgemap.app.ui.theme.OnSurface
import com.knowledgemap.app.ui.theme.Primary
import com.knowledgemap.app.ui.theme.Surface

@Composable
fun EmberBottomNavBar(
    navController: NavHostController,
    hasGaps: Boolean = false
) {
    val screens = listOf(
        BottomBarScreen.Home,
        BottomBarScreen.Graph,
        BottomBarScreen.Quiz,
        BottomBarScreen.Profile
    )
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentDestination = navBackStackEntry?.destination

    NavigationBar(
        containerColor = Background,
        contentColor = Primary,
        modifier = Modifier.testTag("bottom_nav")
    ) {
        screens.forEach { screen ->
            AddItem(
                screen = screen,
                currentDestination = currentDestination,
                navController = navController,
                hasBadge = screen is BottomBarScreen.Quiz && hasGaps
            )
        }
    }
}

@Composable
fun RowScope.AddItem(
    screen: BottomBarScreen,
    currentDestination: NavDestination?,
    navController: NavHostController,
    hasBadge: Boolean
) {
    val selected = currentDestination?.hierarchy?.any {
        it.route == screen.route
    } == true

    NavigationBarItem(
        modifier = Modifier.testTag("nav_item_${screen.route}"),
        label = {
            Text(text = screen.title)
        },
        icon = {
            BadgedBox(
                badge = {
                    if (hasBadge) {
                        Badge(containerColor = Error)
                    }
                }
            ) {
                Image(
                    painter = painterResource(id = screen.iconRes),
                    contentDescription = screen.title,
                    modifier = Modifier.size(24.dp),
                    colorFilter = ColorFilter.tint(
                        if (selected) Primary else OnSurface
                    )
                )
            }
        },
        selected = selected,
        onClick = {
            navController.navigate(screen.route) {
                popUpTo(navController.graph.findStartDestination().id) {
                    saveState = true
                }
                launchSingleTop = true
                restoreState = true
            }
        },
        colors = NavigationBarItemDefaults.colors(
            selectedIconColor = Primary,
            selectedTextColor = Primary,
            unselectedIconColor = OnSurface,
            unselectedTextColor = OnSurface,
            indicatorColor = Surface
        )
    )
}
