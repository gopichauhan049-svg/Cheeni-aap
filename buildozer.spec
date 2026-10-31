[app]

title = Chini Assistant

package.name = chiniassistant

package.domain = org.chini

source.dir = .

source.include_exts = py,png,jpg,kv,atlas,ttf

version = 0.2

requirements = python3,kivy,plyer,requests,pyjnius

android.archs = arm64-v8a

android.permissions = INTERNET,RECORD_AUDIO

android.api = 33

android.minapi = 21

android.accept_sdk_license = True

[buildozer]

log_level = 2

warn_on_root = 1
