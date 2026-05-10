package com.knowledgemap.app.ui

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.knowledgemap.app.ui.components.EmberBottomNavBar
import com.knowledgemap.app.ui.navigation.NavGraph
import com.knowledgemap.app.ui.navigation.Screen
import com.knowledgemap.app.ui.navigation.isBottomNavRoute
import com.knowledgemap.app.ui.navigation.isFullScreenRoute
import com.knowledgemap.app.ui.theme.KnowledgeMapTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            KnowledgeMapTheme {
                MainScreen()
            }
        }
    }
}

@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val navBackStackEntry by navController.currentBackStackEntryAsState()
    val currentRoute = navBackStackEntry?.destination?.route

    Surface(
        modifier = Modifier.fillMaxSize(),
        color = MaterialTheme.colorScheme.background
    ) {
        Scaffold(
            bottomBar = {
                if (isBottomNavRoute(currentRoute) && !isFullScreenRoute(currentRoute)) {
                    EmberBottomNavBar(
                        navController = navController,
                        hasGaps = false
                    )
                }
            }
        ) { paddingValues ->
            NavGraph(
                navController = navController,
                modifier = Modifier.padding(paddingValues),
                startDestination = Screen.Onboarding.route
            )
        }
    }
}
