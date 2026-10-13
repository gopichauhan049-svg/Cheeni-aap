[app]

# (str) Title of your application
title = Chini Assistant

# (str) Package name
package.name = chiniassistant

# (str) Package domain (needed for android packaging)
package.domain = org.chini

# (str) Source directory where the application files are located
source.dir = .

# (list) Source files to include (let it match py,png,jpg,kv,ttf etc.)
source.include_exts = py,png,jpg,kv,atlas,ttf

# (str) Application versioning
version = 0.1

# (list) Application requirements
requirements = python3,kivy,plyer,requests

# (str) Customized icon
#icon.filename = %(source.dir)s/data/icon.png

# (list) Permissions
android.permissions = INTERNET, RECORD_AUDIO

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (bool) Use the Android SDK license agreement
android.accept_sdk_license = True
