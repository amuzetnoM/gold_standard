package com.goldstandard

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Application class for Gold Standard app.
 * Annotated with @HiltAndroidApp to enable Hilt dependency injection.
 */
@HiltAndroidApp
class GoldStandardApp : Application()
