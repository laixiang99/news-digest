# ============================================================
# 📰 每日新闻归纳助手 — 主程序
# ============================================================
# 使用方法：双击运行即可
# 首次使用请先配置 config.json 中的 API 密钥
# ============================================================

import json
import os
import sys
import time
import webbrowser
from datetime import datetime, date

# ---------- 第三方库（需要安装）----------
import subprocess

_REQUIRED_PACKAGES = ["requests", "beautifulsoup4", "feedparser"]

def _ensure_deps():
    """检查并自动安装所需依赖库"""
    missing = []
    for pkg in ["requests", "bs4", "feedparser"]:
        try:
            __import__(pkg.replace("bs4", "bs4"))
        except ImportError:
            missing.append(pkg)
    if not missing:
        return
    print("=" * 50)
    print("📦 首次使用需要安装依赖库（只需一次）")
    print("正在自动安装，请稍候……")
    print("=" * 50)
    # 把 bs4 映射回 beautifulsoup4
    pip_pkgs = [{"bs4": "beautifulsoup4"}.get(p, p) for p in missing]
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install"] + pip_pkgs + ["--quiet"],
            timeout=120
        )
        print("✅ 依赖安装完成！\n")
    except Exception as e:
        print(f"❌ 自动安装失败: {e}")
        print("请手动运行以下命令安装：")
        print(f'   {sys.executable} -m pip install requests beautifulsoup4 feedparser')
        input("\n按回车键退出...")
        sys.exit(1)

_ensure_deps()

# 修复 Windows 终端中文/emoji 显示问题
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1, errors='replace')

import requests
from bs4 import BeautifulSoup
import feedparser as fp

# ============================================================
# 第一部分：配置
# ============================================================

# 配置文件路径（跟本程序在同一个文件夹）
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")

# 默认配置（第一次运行会自动生成）
DEFAULT_CONFIG = {
    "deepseek_api_key": "",
    "max_news_per_category": 10,   # 每类最多保留几条
    "max_news_total": 50           # 全部累计最多不超过
}

# 新闻分类和数据源
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

# 分类对应的图标
CATEGORY_ICONS = {
    "政治": "🏛️",
    "科技": "💻",
    "AI": "🤖",
    "股票": "📈",
}

# 分类对应的颜色
CATEGORY_COLORS = {
    "政治": "#E74C3C",
    "科技": "#3498DB",
    "AI": "#9B59B6",
    "股票": "#27AE60",
    "抖音热榜": "#FF0050",
    "闲鱼热榜": "#FF6A00"
}

# ============================================================
# 第二部分：读取/创建配置
# ============================================================

def load_config():
    """读取配置文件，如果不存在则创建"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                config = json.load(f)
            return config
        except:
            pass

    # 创建默认配置
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(DEFAULT_CONFIG, f, ensure_ascii=False, indent=2)
    return dict(DEFAULT_CONFIG)


def save_key_to_config(api_key):
    """保存 API 密钥到配置"""
    config = load_config()
    config["deepseek_api_key"] = api_key
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
    print(f"✅ 密钥已保存至: {CONFIG_FILE}")


# ============================================================
# 第三部分：抓取新闻
# ============================================================

def fetch_rss(url, source_name, timeout=15):
    """抓取单个 RSS 源"""
    articles = []
    try:
        print(f"   📡 正在抓取: {source_name} ...", end="")
        feed = fp.parse(url)
        if feed.bozo and not feed.entries:
            print(f" ❌ 失败")
            return articles

        count = 0
        for entry in feed.entries[:10]:  # 每个源最多取10条
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = entry.get("summary", entry.get("description", "")).strip()
            # 去除 HTML 标签
            summary = BeautifulSoup(summary, "html.parser").get_text()[:200] if summary else ""

            if title:
                articles.append({
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "source": source_name,
                })
                count += 1
        print(f" ✅ 获取 {count} 条")
    except Exception as e:
        print(f" ❌ 出错: {str(e)[:30]}")
    return articles


def fetch_all_news():
    """抓取所有分类的新闻"""
    all_news = {}
    total = 0

    print("\n" + "=" * 50)
    print("📡 第一步：正在抓取新闻……")
    print("（部分源可能失效，能抓到多少算多少）")
    print("=" * 50)

    for category, sources in NEWS_SOURCES.items():
        print(f"\n📂 【{category}】分类:")
        category_articles = []
        for source in sources:
            articles = fetch_rss(source["url"], source["name"])
            category_articles.extend(articles)
        all_news[category] = category_articles
        total += len(category_articles)
        print(f"   📊 共收集 {len(category_articles)} 条")

    print(f"\n📊 总计抓取 {total} 条新闻")
    return all_news


# ============================================================
# 第四部分：用 DeepSeek AI 归纳总结
# ============================================================

def call_deepseek(api_key, messages, max_retries=3):
    """调用 DeepSeek API"""
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.3,       # 低温度让输出更稳定
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
                print(f"  ⚠️  API 返回错误 {resp.status_code}，重试中...")
                time.sleep(2)
        except Exception as e:
            print(f"  ⚠️  网络错误: {str(e)[:40]}，重试中...")
            time.sleep(3)
    return None


def summarize_category(api_key, category, articles):
    """让 AI 对某一类新闻进行总结和排序"""
    if not articles:
        return []

    print(f"\n🤖 【{category}】正在用 AI 分析 {len(articles)} 条新闻……")

    # 构造给 AI 的提示词
    news_list = []
    for i, article in enumerate(articles, 1):
        news_list.append(f"{i}. 标题：{article['title']}")
        news_list.append(f"   来源：{article['source']}")
        if article['summary']:
            news_list.append(f"   摘要：{article['summary'][:150]}")

    prompt = f"""你是一个专业的新闻编辑。请分析以下 {category} 领域的新闻，完成两项任务：

一、**为每条新闻写一句话总结**（20字以内，简洁有力）

二、**按重要性排序**：哪条最重要、哪条次之

请按以下 JSON 格式输出（不要加任何其他文字）：

```json
[
  {{
    "rank": 1,
    "summary": "一句话总结",
    "reason": "为什么重要（10字以内）"
  }},
  ...
]
```

注意：
- 最多保留10条最重要的新闻
- 如果新闻质量差或明显是广告，跳过
- 排序严格按重要性，最重要的排最前面

以下是需要分析的新闻：

{chr(10).join(news_list)}
"""

    messages = [
        {"role": "system", "content": "你是一个专业的新闻编辑助手，擅长提炼新闻要点并按重要性排序。"},
        {"role": "user", "content": prompt}
    ]

    result = call_deepseek(api_key, messages)
    if result == "API_KEY_ERROR":
        return "API_KEY_ERROR"
    if not result:
        return None

    # 解析 JSON
    try:
        # 从内容中提取 JSON 部分
        json_text = result
        if "```json" in json_text:
            json_text = json_text.split("```json")[1].split("```")[0]
        elif "```" in json_text:
            json_text = json_text.split("```")[1].split("```")[0]

        ranked = json.loads(json_text.strip())

        # 将排序结果附加到文章上
        output = []
        for item in ranked:
            idx = item.get("rank", 1) - 1
            if 0 <= idx < len(articles):
                article = articles[idx].copy()
                article["ai_summary"] = item.get("summary", "")
                article["ai_reason"] = item.get("reason", "")
                output.append(article)
            else:
                # 如果 rank 不匹配，尝试按顺序配对
                pass

        # 如果按 rank 配对不理想，直接按返回顺序
        if not output and len(ranked) > 0:
            for i, item in enumerate(ranked):
                if i < len(articles):
                    article = articles[i].copy()
                    article["ai_summary"] = item.get("summary", "")
                    article["ai_reason"] = item.get("reason", "")
                    output.append(article)

        print(f"  ✅ AI 分析完成，精选 {len(output)} 条")
        return output

    except Exception as e:
        print(f"  ⚠️  AI 返回格式解析失败: {str(e)[:50]}")
        print(f"  原始返回: {result[:200]}")
        # 失败时退回原文
        for article in articles:
            article["ai_summary"] = article["summary"][:30] + "..." if article["summary"] else ""
            article["ai_reason"] = ""
        return articles[:10]


# ============================================================
# 第五部分：生成 HTML 榜单
# ============================================================

def generate_html(all_results, today_str):
    """生成暖色横向风格的 HTML 页面"""
    total = sum(len(items) for items in all_results.values())

    # 暖色配色方案
    CATEGORY_STYLES = {
        "政治": {"icon": "🏛️", "color": "#D35400", "bg": "#FFF3E6"},
        "科技": {"icon": "💻", "color": "#E67E22", "bg": "#FFF8EE"},
        "AI":   {"icon": "🤖", "color": "#8E44AD", "bg": "#F8EFFF"},
        "股票": {"icon": "📈", "color": "#D4AC0D", "bg": "#FFFEF5"},
    }

    # 构建每个分类的 HTML 卡片
    all_cards = ""
    for category in ["AI", "科技", "闲鱼热榜", "抖音热榜", "政治", "股票"]:
        articles = all_results.get(category, [])
        if not articles:
            continue

        style = CATEGORY_STYLES.get(category, {"icon": "📰", "color": "#888", "bg": "#f5f5f5"})
        icon = style["icon"]
        color = style["color"]
        bg = style["bg"]

        # 分类内的新闻列表
        news_html = ""
        for i, article in enumerate(articles):
            title = article.get("title", "无标题")
            link = article.get("link", "#")
            source = article.get("source", "未知")
            summary = article.get("ai_summary", "") or article.get("summary", "")[:40]
            reason = article.get("ai_reason", "")

            # 排名徽章
            if i == 0:
                badge = "🥇"
            elif i == 1:
                badge = "🥈"
            elif i == 2:
                badge = "🥉"
            else:
                badge = f"{i+1}"

            news_html += f"""
            <div class="news-row">
                <div class="nr-badge" style="color:{color}">{badge}</div>
                <div class="nr-body">
                    <a class="nr-title" href="{link}" target="_blank">{title}</a>
                    <div class="nr-meta">
                        <span class="nr-source">{source}</span>
                        {f'<span class="nr-reason">{reason}</span>' if reason else ''}
                    </div>
                </div>
            </div>"""

        # 整个分类卡片
        all_cards += f"""
    <div class="cat-card" style="border-top:4px solid {color};background:{bg};">
        <div class="cat-head">
            <span class="cat-icon">{icon}</span>
            <span class="cat-name" style="color:{color}">{category}</span>
            <span class="cat-count">{len(articles)}</span>
        </div>
        <div class="cat-body">
            {news_html}
        </div>
    </div>"""

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>📰 每日新闻榜单 — {today_str}</title>
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        body {{
            font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
            background: #FDF6EC;
            min-height: 100vh;
            padding: 30px;
        }}
        .wrap {{ max-width:1200px; margin:0 auto; }}

        /* ---- 头部 ---- */
        .head {{
            background: linear-gradient(135deg, #E67E22, #D35400);
            color: #fff;
            border-radius: 18px;
            padding: 32px 40px;
            margin-bottom: 32px;
            box-shadow: 0 6px 24px rgba(211,84,0,0.25);
        }}
        .head h1 {{ font-size:30px; font-weight:700; margin-bottom:6px; }}
        .head .sub {{ font-size:14px; opacity:.8; }}
        .head .date {{ font-size:13px; opacity:.65; margin-top:6px; }}

        /* ---- 分类网格（横向2列） ---- */
        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 22px;
        }}
        @media (max-width:800px) {{
            .grid {{ grid-template-columns: 1fr; }}
            body {{ padding:16px; }}
            .head {{ padding:24px 20px; }}
        }}

        /* ---- 分类卡片 ---- */
        .cat-card {{
            border-radius: 14px;
            box-shadow: 0 2px 12px rgba(0,0,0,.06);
            overflow: hidden;
            transition: transform .2s;
        }}
        .cat-card:hover {{ transform:translateY(-2px); box-shadow:0 6px 20px rgba(0,0,0,.1); }}
        .cat-head {{
            display:flex; align-items:center; gap:10px;
            padding:16px 20px;
            border-bottom:1px solid rgba(0,0,0,.06);
        }}
        .cat-icon {{ font-size:22px; }}
        .cat-name {{ font-size:18px; font-weight:700; }}
        .cat-count {{
            margin-left:auto;
            font-size:13px;
            background:rgba(0,0,0,.06);
            padding:2px 12px;
            border-radius:20px;
            color:#666;
        }}

        /* ---- 新闻条目（横向排列） ---- */
        .cat-body {{ padding:8px 16px 12px; }}
        .news-row {{
            display:flex;
            align-items:flex-start;
            gap:12px;
            padding:12px 8px;
            border-bottom:1px solid rgba(0,0,0,.04);
        }}
        .news-row:last-child {{ border-bottom:none; }}
        .nr-badge {{
            flex-shrink:0;
            width:28px;
            font-size:16px;
            font-weight:700;
            text-align:center;
            line-height:28px;
        }}
        .nr-body {{ flex:1; min-width:0; }}
        .nr-title {{
            display:block;
            font-size:15px;
            font-weight:600;
            color:#3D2B1F;
            text-decoration:none;
            line-height:1.4;
            margin-bottom:4px;
        }}
        .nr-title:hover {{ color:#D35400; text-decoration:underline; }}
        .nr-meta {{
            font-size:12px;
            color:#999;
            display:flex;
            gap:12px;
        }}

        /* ---- 底部 ---- */
        .foot {{
            text-align:center;
            color:#ccc;
            font-size:12px;
            padding:30px 0 10px;
        }}
    </style>
</head>
<body>
<div class="wrap">

    <div class="head">
        <h1>📰 每日新闻榜单</h1>
        <div class="sub">🤖 AI 智能精选 · {total} 条今日要闻</div>
        <div class="date">{today_str}</div>
    </div>

    <div class="grid">
        {all_cards}
    </div>

    <div class="foot">由 AI 新闻归纳助手自动生成 · 每日更新</div>

</div>
</body>
</html>"""

    return html
def check_api_key(config):
    """检查 API 密钥是否已配置"""
    api_key = config.get("deepseek_api_key", "")
    if not api_key:
        print("=" * 50)
        print("⚠️  还没有配置 API 密钥！")
        print("=" * 50)
        print("")
        print("请按照以下步骤操作：")
        print("")
        print("1️⃣  打开网页：https://platform.deepseek.com/")
        print("2️⃣  注册账号并登录")
        print("3️⃣  进入 API Keys 页面，点「创建 API Key」")
        print("4️⃣  复制密钥（以 sk- 开头）")
        print("5️⃣  粘贴到下面即可")
        print("")
        key = input("👉 请输入你的 DeepSeek API 密钥: ").strip()
        if key:
            save_key_to_config(key)
            return key
        else:
            print("❌ 未输入密钥，程序退出。")
            sys.exit(1)
    return api_key


# ============================================================
# 第七部分：主程序入口
# ============================================================

def main():
    print()
    print("🌟" + "=" * 46 + "🌟")
    print("  📰  每日新闻归纳助手 v1.0")
    print("🌟" + "=" * 46 + "🌟")

    # 1. 加载配置
    config = load_config()

    # 2. 检查 API 密钥
    api_key = check_api_key(config)

    # 3. 设置路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_dir = script_dir  # 输出到程序所在目录

    # 4. 抓取新闻
    all_news = fetch_all_news()
    if not all_news or sum(len(v) for v in all_news.values()) == 0:
        print("\n❌ 没有抓取到任何新闻，请检查网络连接后重试")
        input("\n按回车键退出...")
        return

    # 5. AI 分析
    print("\n" + "=" * 50)
    print("🤖 第二步：AI 正在分析新闻……")
    print("=" * 50)

    all_results = {}
    has_error = False
    for category, articles in all_news.items():
        if articles:
            result = summarize_category(api_key, category, articles)
            if result == "API_KEY_ERROR":
                print("\n❌ API 密钥无效！请重新配置")
                print(f"请打开 {CONFIG_FILE} 修改密钥，或重新运行程序")
                has_error = True
                break
            elif result is None:
                print(f"  ⚠️  AI 分析失败，使用原始数据")
                result = articles[:10]
            all_results[category] = result
        else:
            all_results[category] = []

    if has_error:
        input("\n按回车键退出...")
        return

    # 6. 生成 HTML
    print("\n" + "=" * 50)
    print("📄 第三步：正在生成榜单……")
    print("=" * 50)

    today = date.today()
    today_str = f"{today.year}年{today.month}月{today.day}日"
    filename = f"新闻榜单_{today.year}-{today.month:02d}-{today.day:02d}.html"
    output_path = os.path.join(output_dir, filename)

    html = generate_html(all_results, today_str)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ 榜单已生成！")
    print(f"📄 文件位置: {output_path}")

    # 7. 自动打开浏览器
    try:
        webbrowser.open(f"file://{output_path}")
        print("🌐 已自动在浏览器中打开")
    except:
        print(f"📌 请手动双击文件打开")

    print("\n" + "=" * 50)
    print("🎉 完成！明天见~")
    print("=" * 50)

    input("\n按回车键退出...")


if __name__ == "__main__":
    main()








