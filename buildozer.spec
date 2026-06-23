# ============================================================
# Buildozer 配置文件 — 将 Python 打包为 Android APK
# ============================================================

[app]

# 应用名称
title = 新闻归纳助手

# 包名 (Android 唯一标识)
package.name = newsdigest

# 包域名 (反向域名格式)
package.domain = com.newsdigest

# 源码目录
source.dir = .

# 入口脚本
source.main = main.py

# 版本号
version = 1.0.0

# 版本代码 (给 Google Play 用)
version.code = 1

# 最低 SDK 版本 (Android 8.0+)
android.api = 29

# 目标 SDK 版本
android.api_level = 33

# Android NDK 版本
android.ndk = 27c

# 支持的架构
android.archs = arm64-v8a, armeabi-v7a

# 权限
android.permissions = INTERNET, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE
# android.gradle_dependencies =

# 应用图标
android.icon = static/icons/icon-512.png

# 允许 HTTP 明文 (本地通信需要)
android.manifest.android_uses_cleartext_traffic = True

# 使用 SDL2 (Kivy 需要)
android.use_sdl2 = True

# 包含的 Python 模块
requirements = python3,flask,flask-cors,requests,beautifulsoup4,feedparser,kivy

# 排除不必要的模块减小 APK 体积
android.exclude_so = x86, x86_64

# 是否为私有存储 (避免文件泄露)
android.private_storage = True

# APK 输出名
android.filename = 新闻归纳助手

# 使用 Java 17
android.java_version = 17

# 开启日志
android.logcat_filter_whitelist = python, flask

[buildozer]

# 日志级别
log_level = 2

# 构建目录
build_dir = ./.buildozer

# 二进制输出目录
bin_dir = ./bin

# 使用 WSL (Windows 上构建)
warn_on_root = True

# 在 CI 上自动接受 Android 许可
android.accept_sdk_license = True



