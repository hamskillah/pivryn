import java.security.MessageDigest
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.kotlin.compose)
    alias(libs.plugins.kotlin.serialization)
}

android {
    namespace = "com.zosma.pocketpi"
    compileSdk = 34

    defaultConfig {
        // A separate package is permitted only with a verified *source-built*
        // Termux bootstrap. Debug compatibility builds retain com.termux.
        // They must never be published or installed beside official Termux.
        applicationId = if (providers.gradleProperty("pivrynCustomPrefix").orNull == "true")
            "com.pivryn" else "com.termux"
        minSdk = 24
        // CRITICAL: Termux itself caps targetSdk at 28. Android 10+ enforces
        // W^X on the app's private data directory when targetSdk >= 29 — any
        // execve() of a file under /data/user/0/<pkg>/files/ is blocked with
        // EACCES regardless of file mode bits. Capping at 28 keeps the
        // legacy semantics that allow exec from app-data, which Pi (and the
        // entire Termux runtime) relies on.
        targetSdk = 28
        versionCode = 7
        versionName = "0.1.0-dev"

        ndk { abiFilters += listOf("arm64-v8a") }
    }

    // Executable Termux app-data paths require targetSdk 28 on current Android.
    // Lint's Play Store target age warning is documented as a deliberate
    // compatibility limitation; do not publish to Play without fixing it.
    lint {
        disable += "ExpiredTargetSdkVersion"
    }

    // Pivryn currently mirrors the upstream Termux's install layout — the bootstrap zip extracts
    // into /data/data/com.zosma.pocketpi/files/usr at first launch.
    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
        debug { /* defaults */ }
    }

    // Ship the bootstrap zip as a raw asset; PocketPiBootstrap unzips on first
    // run. The build script in bootstrap/build-bootstrap.sh produces this.
    sourceSets["main"].assets.srcDir("../../bootstrap/dist")

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }

    packaging {
        resources.excludes += listOf("/META-INF/{AL2.0,LGPL2.1}", "/META-INF/INDEX.LIST")
        // Required when AndroidManifest sets extractNativeLibs="true". Pocket
        // Pi needs that flag so .so files end up in nativeLibraryDir with
        // executable permission, which is the only reliable way to ship
        // executables to the device on Android 6+.
        jniLibs.useLegacyPackaging = true
    }
}

// Production release must refuse the official Termux prefix. A separate app
// identity without matching native binaries breaks apt, Node and shell tools.
val verifyPivrynReleaseBootstrap = tasks.register("verifyPivrynReleaseBootstrap") {
    doLast {
        if (providers.gradleProperty("pivrynCustomPrefix").orNull != "true") {
            throw GradleException("Pivryn release blocked: custom-prefix bootstrap not enabled.")
        }
        val meta = file("../../bootstrap/dist/.pivryn-custom-prefix")
        val zip = file("../../bootstrap/dist/bootstrap-aarch64.zip")
        if (!meta.isFile || !zip.isFile) {
            throw GradleException("Pivryn release blocked: custom-prefix archive or metadata missing.")
        }
        val lines = meta.readLines()
        if (lines.size != 2 || lines[0] != "com.pivryn") {
            throw GradleException("Pivryn release blocked: malformed package marker.")
        }
        val digest = MessageDigest.getInstance("SHA-256")
        val sha = digest.digest(zip.readBytes()).joinToString("") { "%02x".format(it) }
        if (sha != lines[1].trim()) {
            throw GradleException("Pivryn release blocked: custom-prefix bootstrap checksum mismatch.")
        }
    }
}
tasks.matching { it.name == "preReleaseBuild" }.configureEach {
    dependsOn(verifyPivrynReleaseBootstrap)
}

dependencies {
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.lifecycle.runtime)
    implementation(libs.androidx.activity.compose)
    implementation(platform(libs.androidx.compose.bom))
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)
    implementation(libs.androidx.datastore)
    implementation(libs.androidx.work)
    implementation(libs.kotlinx.serialization.json)
    implementation(libs.kotlinx.coroutines.android)
    implementation(libs.androidx.camera.core)
    implementation(libs.androidx.camera.camera2)
    implementation(libs.androidx.camera.lifecycle)
}
