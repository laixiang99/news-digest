@echo off
chcp 65001 >nul
title 📱 新闻归纳助手 - APK 构建工具

echo ================================================
echo   📱  每日新闻归纳助手 — APK 构建向导
echo ================================================
echo.
echo 本工具将帮你把 Python 程序打包成 Android APK
echo.
echo 请选择构建方式：
echo.
echo   [1] 使用 WSL + Buildozer 本地构建（推荐）
echo       需要：Windows 10/11 + WSL Ubuntu
echo       耗时：首次约 30 分钟
echo.
echo   [2] 使用 GitHub Actions 在线构建
echo       需要：GitHub 账号
echo       耗时：约 15 分钟
echo.
echo   [3] 使用 Docker 部署为网页服务（无需 APK）
echo       需要：任意云服务商账号
echo       耗时：约 5 分钟
echo.
set /p CHOICE="请输入选项 (1/2/3): "

if "%CHOICE%"=="1" goto wsl
if "%CHOICE%"=="2" goto github
if "%CHOICE%"=="3" goto cloud
goto end

:wsl
echo.
echo ================================================
echo   方式 1：WSL + Buildozer 本地构建
echo ================================================
echo.
echo 步骤：
echo   1. 确保已安装 WSL
echo      管理员 PowerShell: wsl --install -d Ubuntu
echo.
echo   2. 重启电脑
echo.
echo   3. 打开 WSL 终端:
echo      wsl -d Ubuntu
echo.
echo   4. 在 WSL 中运行:
echo      cd /mnt/d/codex/新闻归纳助手
echo      bash build-apk-wsl.sh
echo.
echo   5. 构建完成后，APK 在 bin\ 目录下
echo      复制到手机安装即可
echo.
echo 注意：首次构建需要下载 Android SDK/NDK
echo       请确保网络畅通，预计需要 20-40 分钟
echo.
echo 支持设备：
echo   - 小米 / 红米 (MIUI / HyperOS)
echo   - 华为 (HarmonyOS)
echo   - 荣耀 (MagicOS)
echo   - OPPO / vivo / 一加
echo   - 三星 / 其他 Android 8.0+ 设备
echo.
pause
goto end

:github
echo.
echo ================================================
echo   方式 2：GitHub Actions 在线构建
echo ================================================
echo.
echo 步骤：
echo   1. 在 GitHub 创建仓库
echo      https://github.com/new
echo.
echo   2. 上传代码（在项目目录运行）:
echo      cd D:\codex\新闻归纳助手
echo      git init
echo      git add .
echo      git commit -m "init"
echo      git remote add origin https://github.com/你的用户名/新闻归纳助手.git
echo      git push -u origin main
echo.
echo   3. 手动触发构建：
echo      打开 GitHub 仓库 → Actions
echo      选择「构建 Android APK」→ Run workflow
echo.
echo   4. 等待 15 分钟，下载 APK
echo.
echo   5. 可以打标签自动发布:
echo      git tag v1.0.0
echo      git push origin v1.0.0
echo.
pause
goto end

:cloud
echo.
echo ================================================
echo   方式 3：Docker 云部署（无需 APK）
echo ================================================
echo.
echo 此方式不需要 APK，直接部署为网页服务
echo 家人通过浏览器即可使用
echo.
echo 推荐平台（有免费额度）：
echo   - Render.com: render.yaml 一键部署
echo   - Railway.app: 连接 GitHub 自动部署
echo   - 阿里云/腾讯云: 国内访问更快
echo.
echo 部署步骤：
echo   1. 上传代码到 GitHub
echo   2. 在 Render 选择 Deploy from Git
echo   3. 连接仓库，选择 Docker 部署
echo   4. 几分钟后即可通过网页访问
echo   5. 手机浏览器添加到桌面（PWA）
echo.
pause
goto end

:end
echo.
echo 按任意键退出...
pause >nul
