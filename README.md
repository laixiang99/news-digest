# 📰 每日新闻归纳助手

> **每天3分钟，AI帮你读懂天下事** — 支持小米、红米、华为、荣耀等主流手机

## 快速开始

### 方式一：📱 Android APK（推荐给家人）

1. **使用 WSL 本地构建**（需要 Windows 10/11）
   ```bash
   # 管理员 PowerShell: 安装 WSL
   wsl --install -d Ubuntu
   # 重启后进入 WSL
   wsl -d Ubuntu
   cd /mnt/d/codex/新闻归纳助手
   bash build-apk-wsl.sh
   ```
   构建完成后 APK 文件在 `bin/` 目录，复制到手机安装

2. **或使用 GitHub Actions 在线构建**
   - 推送代码到 GitHub
   - 在 Actions 页面手动触发构建
   - 下载 APK 分享给家人

### 方式二：🌐 云服务器部署（无需 APK）

部署到 Render/Railway 等免费云服务，家人通过浏览器访问即可。

```bash
# 本地测试
pip install -r requirements.txt
python server.py
# 打开 http://localhost:5000
```

### 方式三：💻 本地服务器（同一 Wi-Fi 可用）

在电脑上运行后，局域网内任何手机均可访问。

```bash
python server.py
# 手机访问 http://电脑IP:5000
```

## 项目结构

```
新闻归纳助手/
├── server.py              # 🆕 Web API 服务器（核心）
├── news_digest.py         # 原版 CLI 程序（保留）
├── config.json            # 配置文件
├── requirements.txt       # 🆕 Python 依赖
├── Dockerfile             # 🆕 Docker 部署配置
├── render.yaml            # 🆕 Render 云部署配置
├── buildozer.spec         # 🆕 APK 构建配置
├── build-apk-wsl.sh       # 🆕 WSL 构建脚本
├── 构建APK向导.bat         # 🆕 构建向导
├── static/
│   ├── index.html         # 🆕 移动端 PWA 首页
│   ├── manifest.json      # 🆕 PWA 配置
│   ├── sw.js              # 🆕 离线缓存支持
│   └── icons/             # 🆕 应用图标
└── .github/workflows/
    └── build-apk.yml      # 🆕 GitHub Actions 自动构建
```

## 功能特性

| 功能 | 说明 |
|------|------|
| 📡 **多源聚合** | 新华网、人民网、36氪、IT之家等 20+ 新闻源 |
| 🤖 **AI 总结** | DeepSeek 智能归纳，一句话看懂每条新闻 |
| 📱 **移动优先** | PWA 设计，支持所有 Android/iOS 设备 |
| 🌙 **深色模式** | 跟随系统自动切换 |
| 📶 **离线可用** | Service Worker 缓存支持 |
| 🔄 **自动更新** | 每次打开自动获取最新新闻 |
| 🏪 **分类浏览** | 政治、科技、AI、股票、抖音、闲鱼 |

## 配置说明

1. 获取 [DeepSeek API Key](https://platform.deepseek.com/)
2. 打开应用 → 点击右上角 ⚙️ → 输入密钥
3. 开始使用 AI 智能新闻归纳

## 技术栈

- **后端**: Python + Flask + DeepSeek API
- **前端**: 纯 HTML/CSS/JS PWA
- **打包**: Buildozer + Python-for-Android
- **部署**: Docker / Render / Railway

## 兼容设备

| 品牌 | 系统 | 支持 |
|------|------|------|
| 小米 / 红米 | MIUI / HyperOS | ✅ |
| 华为 | HarmonyOS / EMUI | ✅ |
| 荣耀 | MagicOS | ✅ |
| OPPO / 一加 | ColorOS | ✅ |
| vivo / iQOO | OriginOS | ✅ |
| 三星 | One UI | ✅ |
| 其他 | Android 8.0+ | ✅ |

## 许可证

MIT
