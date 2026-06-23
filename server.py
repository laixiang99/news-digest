# ============================================================
# 📰 每日新闻归纳助手 — Web API 服务器版
# ============================================================
# 支持两种运行模式：
#   1. 本地服务器 (python server.py) — 在电脑上运行，浏览器访问
#   2. 云端部署 — 部署到 Render/Railway 等免费云服务
# ============================================================

import json
import os
import sys
import time
from datetime import datetime, date
from http import HTTPStatus
from functools import wraps

# ---------- 第三方库 ----------
try:
    from flask import (
        Flask, request, jsonify, render_template,
        send_from_directory, Response, stream_with_context
    )
    from flask_cors import CORS
except ImportError:
    print("需要安装依赖库，请运行：")
    print("   pip install flask flask-cors requests beautifulsoup4 feedparser")
    sys.exit(1)

import requests
from bs4 import BeautifulSoup
import feedparser as fp

# ============================================================
# 第一部分：配置
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

DEFAULT_CONFIG = {
    "deepseek_api_key": "",
    "max_news_per_category": 10,
    "max_news_total": 50,
    "server_port": 5000,
    "server_host": "0.0.0.0",
}

NEWS_SOURCES = {
    "政治": [
        {"name": "新华网", "url": "http://www.xinhuanet.com/politics/news_politics.xml"},
        {"name": "人民网", "url": "http://www.people.com.cn/rss/politics.xml"},
        {"name": "中国新闻网", "url": "https://www.chinanews.com.cn/rss/gn.xml"},
        {"name": "观察者网", "url": "https://www.guancha.cn/rss.xml"},
    ],
    "科技": [
        {"name": "36氪", "url": "https://36kr.com/feed"},
        {"name": "IT之家", "url": "https://rss.ithome.com/rss/news.xml"},
        {"name": "新浪科技", "url": "https://rss.sina.com.cn/roll/tech.xml"},
        {"name": "Google科技", "url": "https://news.google.com/rss/search?q=科技+互联网+中国&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"},
    ],
    "AI": [
        {"name": "量子位", "url": "https://www.qbitai.com/feed"},
        {"name": "雷锋网AI", "url": "https://www.leiphone.com/feed/ai"},
        {"name": "机器之心", "url": "https://www.jiqizhixin.com/rss"},
        {"name": "Google AI", "url": "https://news.google.com/rss/search?q=人工智能+AI+中国&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"},
    ],
    "股票": [
        {"name": "Google财经", "url": "https://news.google.com/rss/search?q=股票+股市+A股&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"},
        {"name": "Investing.com", "url": "https://www.investing.com/rss/news.rss"},
        {"name": "同花顺财经", "url": "http://rss.10jqka.com.cn/stock"},
        {"name": "华尔街见闻", "url": "https://wallstreetcn.com/rss/latest"},
    ],
    "抖音热榜": [
        {"name": "抖音热搜", "url": "https://news.google.com/rss/search?q=抖音+热搜+今日热榜+热门&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"},
        {"name": "抖音热门", "url": "https://news.google.com/rss/search?q=抖音+热门+挑战+流行&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"},
        {"name": "抖音网红", "url": "https://news.google.com/rss/search?q=抖音+网红+爆款+热门视频&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"},
    ],
    "闲鱼热榜": [
        {"name": "闲鱼热门", "url": "https://news.google.com/rss/search?q=闲鱼+热门+商品+排行榜&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"},
        {"name": "闲鱼趋势", "url": "https://news.google.com/rss/search?q=闲鱼+二手+最新+爆款&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"},
        {"name": "闲鱼交易", "url": "https://news.google.com/rss/search?q=闲鱼+今日+热门+闲置&hl=zh-CN&gl=CN&ceid=CN:zh-Hans"},
    ],
}

CATEGORY_ICONS = {
    "政治": "🏛️",
    "科技": "💻",
    "AI": "🤖",
    "股票": "📈",
    "抖音热榜": "🔥",
    "闲鱼热榜": "🏪",
}

CATEGORY_COLORS = {
    "政治": "#E74C3C",
    "科技": "#3498DB",
    "AI": "#9B59B6",
    "股票": "#27AE60",
    "抖音热榜": "#FF0050",
    "闲鱼热榜": "#FF6A00",
}
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
    return dict(DEFAULT_CONFIG)


def save_config(updates: dict):
    config = load_config()
    config.update(updates)
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    return config


# ============================================================
# 新闻抓取引擎
# ============================================================

def fetch_rss(url, source_name, timeout=15):
    articles = []
    try:
        feed = fp.parse(url)
        if feed.bozo and not feed.entries:
            return articles
        for entry in feed.entries[:10]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            summary = BeautifulSoup(summary, "html.parser").get_text()[:200] if summary else ""
            published = entry.get("published", entry.get("updated", ""))
            if title:
                articles.append({
                    "title": title, "link": link,
                    "summary": summary, "source": source_name,
                    "published": published,
                })
    except Exception:
        pass
    return articles


def fetch_all_news(max_per_category=10):
    all_news = {}
    totals = {}
    for category, sources in NEWS_SOURCES.items():
        category_articles = []
        for source in sources:
            articles = fetch_rss(source["url"], source["name"])
            category_articles.extend(articles)
        all_news[category] = category_articles[:max_per_category]
        totals[category] = len(category_articles)
    return all_news, totals
# ============================================================
# DeepSeek AI 总结
# ============================================================

def call_deepseek(api_key, messages, max_retries=2):
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 3000,
    }
    for attempt in range(max_retries):
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            elif resp.status_code == 401:
                return "API_KEY_ERROR"
            else:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2)
                continue
            return None
    return None


def summarize_category(api_key, category, articles):
    if not api_key:
        return articles[:5]
    news_text = "\n".join([
        f"{i+1}. {a['title']}（来源：{a['source']}）"
        for i, a in enumerate(articles[:10])
    ])
    messages = [
        {
            "role": "system",
            "content": (
                "你是一个新闻编辑助手。请对以下新闻进行归纳总结。\n"
                "输出 JSON 格式（不要 markdown 代码块标记）：\n"
                "[\n"
                '  {"title": "原标题", "summary": "一句话概括（20字内）", '
                '"highlight": "亮点说明（15字内）"},\n'
                "  ...\n"
                "]\n"
                "要求：保留最重要的新闻，去掉重复和低价值内容，"
                "保持客观中立。返回数组，每一项包含 title/summary/highlight。"
            )
        },
        {"role": "user", "content": f"以下是最新的【{category}】类新闻，请帮我总结：\n\n{news_text}"}
    ]
    result = call_deepseek(api_key, messages)
    if result == "API_KEY_ERROR":
        return result
    if result is None:
        return None
    try:
        cleaned = result.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[1]
            cleaned = cleaned.rsplit("```", 1)[0]
        parsed = json.loads(cleaned)
        return parsed
    except json.JSONDecodeError:
        return None
# ============================================================
# Flask Web 应用
# ============================================================

app = Flask(__name__, static_folder=None)
CORS(app)
config = load_config()


# ---------- API 路由 ----------

@app.route("/api/config", methods=["GET"])
def get_config():
    cfg = load_config()
    cfg.pop("deepseek_api_key", None)
    return jsonify(cfg)


@app.route("/api/config/key", methods=["POST"])
def set_api_key():
    data = request.get_json(force=True)
    key = data.get("key", "").strip()
    if not key:
        return jsonify({"error": "密钥不能为空"}), 400
    save_config({"deepseek_api_key": key})
    return jsonify({"success": True, "message": "密钥已保存"})


@app.route("/api/config/key/status", methods=["GET"])
def check_key_status():
    cfg = load_config()
    has_key = bool(cfg.get("deepseek_api_key", ""))
    return jsonify({"configured": has_key})


@app.route("/api/sources", methods=["GET"])
def get_sources():
    sources = {}
    for category, items in NEWS_SOURCES.items():
        sources[category] = {
            "icon": CATEGORY_ICONS.get(category, "📰"),
            "color": CATEGORY_COLORS.get(category, "#666"),
            "sources": [s["name"] for s in items],
        }
    return jsonify(sources)


@app.route("/api/news/fetch", methods=["POST"])
def fetch_news():
    data = request.get_json(force=True) or {}
    use_ai = data.get("use_ai", True)
    cfg = load_config()
    api_key = cfg.get("deepseek_api_key", "")
    all_news, totals = fetch_all_news(cfg.get("max_news_per_category", 10))
    results = {}
    ai_enabled = use_ai and bool(api_key)
    ai_error = None

    for category, articles in all_news.items():
        if not articles:
            results[category] = []
            continue
        if ai_enabled:
            summarized = summarize_category(api_key, category, articles)
            if summarized == "API_KEY_ERROR":
                ai_error = "API_KEY_INVALID"
                results[category] = articles[:5]
            elif summarized is not None:
                enriched = []
                for i, item in enumerate(summarized):
                    original = articles[i] if i < len(articles) else {}
                    enriched.append({
                        "title": item.get("title", original.get("title", "")),
                        "summary": item.get("summary", ""),
                        "highlight": item.get("highlight", ""),
                        "link": original.get("link", ""),
                        "source": original.get("source", ""),
                    })
                results[category] = enriched
            else:
                results[category] = articles[:5]
        else:
            results[category] = articles[:5]

    return jsonify({
        "categories": results,
        "totals": totals,
        "ai_used": ai_enabled,
        "ai_error": ai_error,
        "timestamp": datetime.now().isoformat(),
        "date_str": date.today().strftime("%Y年%m月%d日"),
    })


@app.route("/api/news/refresh-all", methods=["POST"])
def refresh_all():
    return fetch_news()


# ---------- 静态文件服务 ----------

@app.route("/")
def index():
    return send_from_directory(os.path.join(BASE_DIR, "static"), "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    static_dir = os.path.join(BASE_DIR, "static")
    requested = os.path.normpath(os.path.join(static_dir, filename))
    if not requested.startswith(os.path.normpath(static_dir)):
        return jsonify({"error": "Forbidden"}), 403
    if os.path.isfile(requested):
        return send_from_directory(static_dir, filename)
    icons_dir = os.path.join(BASE_DIR, "static", "icons")
    icon_file = os.path.join(icons_dir, filename)
    if os.path.isfile(icon_file):
        return send_from_directory(icons_dir, filename)
    return jsonify({"error": "Not found"}), 404
# ============================================================
# 启动入口
# ============================================================

def main():
    global config
    config = load_config()
    port = int(os.environ.get("PORT", config.get("server_port", 5000)))
    host = os.environ.get("HOST", config.get("server_host", "0.0.0.0"))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"

    api_key = config.get("deepseek_api_key", "")
    if not api_key:
        print("⚠️  未配置 DeepSeek API 密钥")
        print("   请通过网页界面设置，或编辑 config.json")
        print()

    print("=" * 50)
    print("  📰  每日新闻归纳助手 — 服务器版")
    print("=" * 50)
    print(f"  🌐  启动地址: http://{host}:{port}")
    print(f"  📱  手机访问: http://你的电脑IP:{port}")
    print(f"  📄  配置文件: {CONFIG_FILE}")
    print("=" * 50)
    print("  💡 提示：")
    print("  - 首次使用请先配置 API 密钥")
    print("  - 手机和电脑需要在同一 Wi-Fi 网络下")
    print("  - 按 Ctrl+C 停止服务器")
    print("=" * 50)

    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    main()
