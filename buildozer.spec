[app]
title = Username Runner
package.name = usernamerunner
package.domain = org.demo
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# Kivy aur python3 required hain
requirements = python3,kivy

# Screen orientation
orientation = portrait
fullscreen = 0

# Permissions (agar future me use karne ho)
android.permissions = INTERNET

# Icon (optional)
# icon.filename = %(source.dir)s/icon.png

# Entry point (main file)
main.py = main.py

# Minimum supported SDK version (optional, safe default)
android.minapi = 21

# Target SDK version (GitHub runner ke liye compatible)
android.sdk = 34

# Package format (important for modern builds)
android.archs = armeabi-v7a, arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1

# GitHub Actions environment ke liye in options ko enable karna helpful hota hai
build_dir = .buildozer
bin_dir = bin
