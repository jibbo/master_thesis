#!/bin/bash
./gradlew clean;./gradlew cleanBuildCache; ./gradlew assemble
adb push app/build/outputs/apk/app-debug.apk /sdcard/
cp -v app/build/outputs/apk/app-debug.apk ~/thesis/ArtistGui/app/src/main/assets/codelib/
