[app]
title = HAROLD_FIREWALL
package.name = haroldfirewall
package.domain = uk.harolditdata
source.dir = .
source.include_exts = py,nft,txt
version = 1.0.0
requirements = python3,kivy==2.3.1,pillow
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
log_level = 2

[buildozer]
log_level = 2
warn_on_root = 1
