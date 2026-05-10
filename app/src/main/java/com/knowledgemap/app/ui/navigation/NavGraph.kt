package com.knowledgemap.app.ui.navigation

import androidx.compose.animation.*
import androidx.compose.animation.core.tween
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.knowledgemap.app.ui.screen.assessment.AssessmentScreen
import com.knowledgemap.app.ui.screen.home.HomeScreen
import com.knowledgemap.app.ui.screen.knowledge.KnowledgeMapScreen
import com.knowledgemap.app.ui.screen.onboarding.OnboardingScreen
import com.knowledgemap.app.ui.screen.profile.ProfileScreen
import com.knowledgemap.app.ui.screen.recommendation.RecommendationScreen
import com.knowledgemap.app.ui.screen.session.SessionLoggerScreen


sealed class Screen(val route: String) {
    data object Onboarding : Screen("onboarding")
    data object KnowledgeMap : Screen("knowledge_map")
    data object Assessment : Screen("assessment/{topicId}") {
        fun createRoute(topicId: String) = "assessment/$topicId"
    }
    data object Recommendation : Screen("recommendation")
    data object Session : Screen("session/{topicId}") {
        fun createRoute(topicId: String) = "session/$topicId"
    }
}

val bottomNavRoutes = listOf(
    BottomBarScreen.Home.route,
    BottomBarScreen.Graph.route,
    BottomBarScreen.Quiz.route,
    BottomBarScreen.Profile.route
)

fun isBottomNavRoute(route: String?): Boolean = route in bottomNavRoutes

fun isFullScreenRoute(route: String?): Boolean {
    if (route == null) return false
    return route.startsWith("assessment/") || route.startsWith("session/")
}

@Composable
fun NavGraph(
    navController: NavHostController,
    modifier: Modifier = Modifier,
    startDestination: String = Screen.Onboarding.route
) {
    NavHost(
        navController = navController,
        startDestination = startDestination,
        modifier = modifier,
        enterTransition = {
            slideInHorizontally(initialOffsetX = { 1000 }, animationSpec = tween(400)) + fadeIn(animationSpec = tween(400))
        },
        exitTransition = {
            slideOutHorizontally(targetOffsetX = { -1000 }, animationSpec = tween(400)) + fadeOut(animationSpec = tween(400))
        },
        popEnterTransition = {
            slideInHorizontally(initialOffsetX = { -1000 }, animationSpec = tween(400)) + fadeIn(animationSpec = tween(400))
        },
        popExitTransition = {
            slideOutHorizontally(targetOffsetX = { 1000 }, animationSpec = tween(400)) + fadeOut(animationSpec = tween(400))
        }
    ) {
        // ── Onboarding ──
        composable(Screen.Onboarding.route) {
            OnboardingScreen(
                onComplete = {
                    navController.navigate(BottomBarScreen.Home.route) {
                        popUpTo(Screen.Onboarding.route) { inclusive = true }
                    }
                }
            )
        }

        // ── Bottom Nav: Home ──
        composable(BottomBarScreen.Home.route) {
            HomeScreen()
        }

        // ── Bottom Nav: Knowledge Map ──
        composable(BottomBarScreen.Graph.route) {
            KnowledgeMapScreen(
                onTopicClick = { topicId ->
                    navController.navigate(Screen.Assessment.createRoute(topicId))
                },
                onRecommendationsClick = {
                    navController.navigate(Screen.Recommendation.route)
                }
            )
        }

        // ── Bottom Nav: Tasks / Quiz ──
        composable(BottomBarScreen.Quiz.route) {
            RecommendationScreen(
                onBack = { navController.popBackStack() },
                onTopicClick = { topicId ->
                    navController.navigate(Screen.Assessment.createRoute(topicId))
                }
            )
        }

        // ── Bottom Nav: Profile ──
        composable(BottomBarScreen.Profile.route) {
            ProfileScreen()
        }

        // ── Full-screen: Assessment ──
        composable(
            route = Screen.Assessment.route,
            arguments = listOf(navArgument("topicId") { type = NavType.StringType })
        ) { backStackEntry ->
            val topicId = backStackEntry.arguments?.getString("topicId") ?: ""
            if (topicId.isNotBlank()) {
                AssessmentScreen(
                    topicId = topicId,
                    onBack = { navController.popBackStack() },
                    onComplete = { navController.popBackStack() }
                )
            } else {
                LaunchedEffect(Unit) {
                    navController.popBackStack()
                }
            }
        }

        // ── Full-screen: Recommendation ──
        composable(Screen.Recommendation.route) {
            RecommendationScreen(
                onBack = { navController.popBackStack() },
                onTopicClick = { topicId ->
                    navController.navigate(Screen.Assessment.createRoute(topicId))
                }
            )
        }

        // ── Full-screen: Session Logger ──
        composable(
            route = Screen.Session.route,
            arguments = listOf(navArgument("topicId") { type = NavType.StringType })
        ) { backStackEntry ->
            val topicId = backStackEntry.arguments?.getString("topicId") ?: ""
            if (topicId.isNotBlank()) {
                SessionLoggerScreen(
                    topicId = topicId,
                    onBack = { navController.popBackStack() },
                    onComplete = { navController.popBackStack() }
                )
            } else {
                LaunchedEffect(Unit) {
                    navController.popBackStack()
                }
            }
        }
    }
}
