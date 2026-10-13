[app]
title = Chini Assistant
package.name = chiniassistant
package.domain = org.chini
source.include_exts = py,png,jpg,kv,atlas,ttf
version = 0.1
requirements = python3,kivy,plyer,requests

orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0

android.permissions = INTERNET, RECORD_AUDIO
android.api = 33
android.minapi = 21
android.sdk = 20
android.ndk = 25b
android.accept_sdk_license = True
