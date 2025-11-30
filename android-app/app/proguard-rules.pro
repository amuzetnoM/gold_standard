# Add project specific ProGuard rules here.
# You can control the set of applied configuration files using the
# proguardFiles setting in build.gradle.kts.
#
# For more details, see
#   http://developer.android.com/guide/developing/tools/proguard.html

# Keep data classes for Gson
-keepclassmembers class com.goldstandard.model.** { *; }
-keepclassmembers class com.goldstandard.data.network.** { *; }

# Room
-keep class * extends androidx.room.RoomDatabase
-keep @androidx.room.Entity class *

# Retrofit
-keepattributes Signature
-keepattributes *Annotation*

# MPAndroidChart
-keep class com.github.mikephil.charting.** { *; }
