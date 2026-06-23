import feedparser, requests, re, json

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
print("=== 更多数据源测试 ===\n")

# 1. 抖音热搜 - 尝试 tophub.today 其他路径
urls_to_try = [
    ("热搜聚合(tophub)", "https://tophub.today/"),
    ("热搜聚合(api)", "https://tophub.today/api/rank"),
    ("百度热榜", "https://top.baidu.com/board?tab=realtime"),
]

for name, url in urls_to_try:
    try:
        r = requests.get(url, headers=headers, timeout=10)
        print(f"{name}: HTTP {r.status_code} ({len(r.text)} bytes)")
    except Exception as e:
        print(f"{name}: {str(e)[:30]}")

# 2. 尝试直接搜索"抖音今日热榜"专用
print("\n--- Google News 专项搜索 ---")
for query, label in [("抖音今日热榜 site:douyin.com OR site:iesdouyin.com", "抖音热榜"),
                      ("抖音热搜榜 今日", "抖音热搜"),
                      ("闲鱼 今日热门 排行榜", "闲鱼排行榜")]:
    feed = feedparser.parse(f"https://news.google.com/rss/search?q={requests.utils.quote(query)}&hl=zh-CN&gl=CN&ceid=CN:zh-Hans")
    print(f"  {label}: {len(feed.entries)} 条")
    if feed.entries:
        print(f"    第一条: {feed.entries[0].title[:60]}")

# 3. 试试夸克/搜狗热搜
try:
    r = requests.get("https://news.sogou.com/", headers=headers, timeout=10)
    if r.status_code == 200:
        print(f"\n搜狗新闻: HTTP 200 ({len(r.text)} bytes)")
except Exception as e:
    print(f"\n搜狗新闻: {str(e)[:30]}")
