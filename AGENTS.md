# 新闻归纳助手 — Agent 开发指南

## 项目架构

- `server.py` — Flask API 服务器（主后端）
- `main.py` — Android Kivy 启动器（APK 入口）
- `news_digest.py` — 原桌面版（保留兼容）
- `static/index.html` — PWA 前端（移动端 UI）
- `buildozer.spec` — Android APK 构建配置

## 核心规则

1. **API 优先**：新功能按 REST API 方式添加
2. **移动优先**：前端 UI 必须适配 320px-480px 屏幕
3. **PWA 兼容**：保持 PWA 可安装性
4. **不要修改原版 news_digest.py**（保留备份）
5. **所有静态资源放 static/ 目录**

## 构建流程

- 本地测试：`python server.py` → 浏览器访问
- APK 构建：`bash build-apk-wsl.sh`（WSL Ubuntu）
- 云端部署：推送到 GitHub → Render/Railway 自动部署
