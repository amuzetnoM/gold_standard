package com.goldstandard.ui.navigation

/**
 * Sealed class representing navigation routes in the app.
 */
sealed class Screen(val route: String) {
    data object Dashboard : Screen("dashboard")
    data object Chart : Screen("chart")
    data object Reports : Screen("reports")
    data object ReportDetail : Screen("report_detail/{reportId}") {
        fun createRoute(reportId: Int) = "report_detail/$reportId"
    }
}
