package com.goldstandard.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.goldstandard.ui.chart.ChartScreen
import com.goldstandard.ui.dashboard.DashboardScreen
import com.goldstandard.ui.reports.ReportDetailScreen
import com.goldstandard.ui.reports.ReportsScreen

/**
 * Main navigation host for the Gold Standard app.
 * Defines all navigation routes and their corresponding screens.
 */
@Composable
fun GoldStandardNavHost(
    modifier: Modifier = Modifier
) {
    val navController = rememberNavController()
    
    NavHost(
        navController = navController,
        startDestination = Screen.Dashboard.route,
        modifier = modifier
    ) {
        composable(route = Screen.Dashboard.route) {
            DashboardScreen(
                onNavigateToChart = {
                    navController.navigate(Screen.Chart.route)
                },
                onNavigateToReports = {
                    navController.navigate(Screen.Reports.route)
                }
            )
        }
        
        composable(route = Screen.Chart.route) {
            ChartScreen(
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
        
        composable(route = Screen.Reports.route) {
            ReportsScreen(
                onNavigateBack = {
                    navController.popBackStack()
                },
                onNavigateToDetail = { reportId ->
                    navController.navigate(Screen.ReportDetail.createRoute(reportId))
                }
            )
        }
        
        composable(
            route = Screen.ReportDetail.route,
            arguments = listOf(
                navArgument("reportId") { type = NavType.IntType }
            )
        ) { backStackEntry ->
            val reportId = backStackEntry.arguments?.getInt("reportId") ?: 0
            ReportDetailScreen(
                reportId = reportId,
                onNavigateBack = {
                    navController.popBackStack()
                }
            )
        }
    }
}
