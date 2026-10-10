[app]
title = Chini Assistant
package.name = chini
package.domain = org.chini
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1
requirements = python3,kivy,requests
orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.permissions = INTERNET, RECORD_AUDIO, WAKE_LOCK

[buildozer]
log_level = 2
warn_on_root = 1
