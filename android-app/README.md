# Gold Standard Android MVP

A companion Android application for the Gold Standard quantitative analysis pipeline. This mobile app provides real-time gold price monitoring, chart visualization with technical indicators, and report management.

## Features

- **Real-time Gold Price Display**: Fetches current gold futures (GC=F) price from Yahoo Finance
- **Price Change Tracking**: Shows percentage change from previous close
- **Interactive Charts**: Historical price visualization using MPAndroidChart
- **Technical Indicators**: SMA and RSI overlay support
- **Report Management**: Local storage of analysis reports using Room database
- **Dark Theme**: Gold-accented dark theme for optimal viewing

## Technology Stack

- **Language**: Kotlin 100%
- **UI Framework**: Jetpack Compose with Material 3
- **Architecture**: MVVM with Repository pattern
- **Dependency Injection**: Hilt
- **Networking**: Retrofit + OkHttp
- **Local Storage**: Room Database
- **Charts**: MPAndroidChart
- **Async**: Kotlin Coroutines + Flow

## Project Structure

```
com/goldstandard/
├── GoldStandardApp.kt        # Application class (Hilt entry point)
├── MainActivity.kt           # Main activity with Compose content
├── di/                       # Hilt dependency modules
│   ├── DatabaseModule.kt
│   └── NetworkModule.kt
├── model/                    # Data models
│   ├── Price.kt
│   ├── Report.kt
│   └── IndicatorValues.kt
├── data/
│   ├── network/              # Retrofit API service
│   ├── local/                # Room database
│   ├── repository/           # Data coordination
│   └── indicator/            # Technical indicator calculations
├── ui/
│   ├── dashboard/            # Dashboard screen
│   ├── chart/                # Chart screen with MPAndroidChart
│   ├── reports/              # Reports list and detail screens
│   ├── navigation/           # Navigation routes and NavHost
│   └── theme/                # Material 3 theming
└── viewmodel/                # ViewModels for each screen
```

## Requirements

- Android Studio Hedgehog (2023.1.1) or later
- Android SDK 34 (for compilation)
- Minimum SDK 24 (Android 7.0 Nougat)
- JDK 17

## Building

1. Open the `android-app` folder in Android Studio
2. Sync Gradle files
3. Run on an emulator or device

```bash
cd android-app
./gradlew assembleDebug
```

## Testing

```bash
cd android-app
./gradlew test
```

## API

The app uses Yahoo Finance public API for gold price data:
- Endpoint: `https://query1.finance.yahoo.com/v8/finance/chart/GC=F`
- Data: Gold Futures (GC=F) OHLCV data

## Screenshots

| Dashboard | Chart | Reports |
|-----------|-------|---------|
| Gold price with change % | Historical chart with SMA/RSI | Report list view |

## License

MIT

---

For the main Python-based analysis pipeline, see the [main README](../README.md).
