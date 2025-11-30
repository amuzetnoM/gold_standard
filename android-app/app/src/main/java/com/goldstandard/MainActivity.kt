package com.goldstandard

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.goldstandard.ui.navigation.GoldStandardNavHost
import com.goldstandard.ui.theme.GoldStandardTheme
import dagger.hilt.android.AndroidEntryPoint

/**
 * Main activity serving as the entry point for the app.
 * Uses Jetpack Compose for the UI.
 */
@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            GoldStandardTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    GoldStandardNavHost()
                }
            }
        }
    }
}
