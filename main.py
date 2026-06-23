# ============================================================
# 📱 Android 启动器 — Kivy WebView 包装
# ============================================================
# 作用：在 Android 上启动 Flask 服务器 + 显示 WebView
# Buildozer 入口点
# ============================================================

import os
import sys
import threading
import time

# ---------- Android 专用 ----------
try:
    from android.webview import AndroidWebView
    from android.activity import MainActivity
    from java import PythonJavaClass, jmethod, jvoid
    HAS_ANDROID = True
except ImportError:
    HAS_ANDROID = False

# ---------- Kivy 界面 ----------
try:
    from kivy.app import App
    from kivy.uix.widget import Widget
    from kivy.clock import Clock
    from kivy.core.window import Window
    from kivy.utils import platform
    HAS_KIVY = True
except ImportError:
    HAS_KIVY = False


# ============================================================
# Flask 服务器线程
# ============================================================

def start_server():
    """在后台线程启动 Flask 服务器"""
    # 添加项目目录到路径
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if base_dir not in sys.path:
        sys.path.insert(0, base_dir)

    # 导入并启动 server 模块
    import server as news_server
    # 覆盖配置，监听本地端口
    os.environ["PORT"] = "8765"
    os.environ["HOST"] = "127.0.0.1"
    os.environ["FLASK_DEBUG"] = "0"

    config = news_server.load_config()
    app = news_server.app

    port = int(os.environ.get("PORT", "8765"))
    host = os.environ.get("HOST", "127.0.0.1")

    # 在 Android 上使用 Werkzeug 服务器（不支持 gunicorn）
    app.run(host=host, port=port, debug=False, use_reloader=False)


# ============================================================
# Kivy 应用
# ============================================================

class NewsWebView(Widget):
    """Android WebView 容器"""
    pass


class NewsApp(App):
    """Kivy 应用入口"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.server_thread = None
        self.webview = None

    def build(self):
        if platform != "android":
            # 在桌面测试时直接返回简单提示
            from kivy.uix.label import Label
            return Label(
                text="请在 Android 设备上运行此 APK\n\n"
                     "桌面测试请运行: python server.py",
                halign="center",
                valign="middle",
            )

        Window.clearcolor = (0.1, 0.1, 0.15, 1)
        return NewsWebView()

    def on_start(self):
        if platform != "android":
            return

        # 启动 Flask 服务器
        self.server_thread = threading.Thread(target=start_server, daemon=True)
        self.server_thread.start()

        # 等待服务器启动后加载 WebView
        Clock.schedule_once(self._load_webview, 3)

    def _load_webview(self, dt):
        """加载 WebView 并指向本地 Flask 服务器"""
        if not HAS_ANDROID:
            return

        try:
            webview = AndroidWebView()
            webview.getSettings().setJavaScriptEnabled(True)
            webview.getSettings().setDomStorageEnabled(True)
            webview.getSettings().setAllowFileAccess(True)
            webview.getSettings().setAllowContentAccess(True)

            # 允许混合内容（本地 HTTP）
            webview.getSettings().setMixedContentMode(0)

            # 加载本地服务器
            webview.loadUrl("http://127.0.0.1:8765/")

            # 全屏显示 WebView
            MainActivity.setContentView(webview)
        except Exception as e:
            print(f"❌ WebView 加载失败: {e}")

    def on_pause(self):
        return True

    def on_resume(self):
        pass


# ============================================================
# 主入口
# ============================================================

if __name__ == "__main__":
    NewsApp().run()
