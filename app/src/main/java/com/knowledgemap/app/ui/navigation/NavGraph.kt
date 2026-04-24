package com.knowledgemap.app.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.navArgument
import com.knowledgemap.app.ui.screen.assessment.AssessmentScreen
import com.knowledgemap.app.ui.screen.knowledge.KnowledgeMapScreen
import com.knowledgemap.app.ui.screen.onboarding.OnboardingScreen
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

@Composable
fun NavGraph(
    navController: NavHostController,
    startDestination: String = Screen.Onboarding.route
) {
    NavHost(
        navController = navController,
        startDestination = startDestination
    ) {
        composable(Screen.Onboarding.route) {
            OnboardingScreen(
                onComplete = {
                    navController.navigate(Screen.KnowledgeMap.route) {
                        popUpTo(Screen.Onboarding.route) { inclusive = true }
                    }
                }
            )
        }

        composable(Screen.KnowledgeMap.route) {
            KnowledgeMapScreen(
                onTopicClick = { topicId ->
                    navController.navigate(Screen.Assessment.createRoute(topicId))
                },
                onRecommendationsClick = {
                    navController.navigate(Screen.Recommendation.route)
                }
            )
        }

        composable(
            route = Screen.Assessment.route,
            arguments = listOf(navArgument("topicId") { type = NavType.StringType })
        ) { backStackEntry ->
            val topicId = backStackEntry.arguments?.getString("topicId") ?: ""
            // Validate topicId before navigation
            if (topicId.isNotBlank()) {
                AssessmentScreen(
                    topicId = topicId,
                    onBack = { navController.popBackStack() },
                    onComplete = { navController.popBackStack() }
                )
            } else {
                // Invalid topicId, navigate back
                LaunchedEffect(Unit) {
                    navController.popBackStack()
                }
            }
        }

        composable(Screen.Recommendation.route) {
            RecommendationScreen(
                onBack = { navController.popBackStack() },
                onTopicClick = { topicId ->
                    navController.navigate(Screen.Assessment.createRoute(topicId))
                }
            )
        }

        composable(
            route = Screen.Session.route,
            arguments = listOf(navArgument("topicId") { type = NavType.StringType })
        ) { backStackEntry ->
            val topicId = backStackEntry.arguments?.getString("topicId") ?: ""
            // Validate topicId before navigation
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