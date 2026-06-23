import feedparser, requests, json, re

print("=" * 50)
print("测试数据源...")
print("=" * 50)

# 1. Google News - 抖音热搜
try:
    feed = feedparser.parse("https://news.google.com/rss/search?q=抖音+热搜&hl=zh-CN&gl=CN&ceid=CN:zh-Hans")
    print(f"\n1 Google News(抖音热搜): {len(feed.entries)} 条")
    for e in feed.entries[:3]:
        print(f"   - {e.title[:50]}")
except: print("   ❌ 失败")

# 2. Google News - 闲鱼热门
try:
    feed = feedparser.parse("https://news.google.com/rss/search?q=闲鱼+热门&hl=zh-CN&gl=CN&ceid=CN:zh-Hans")
    print(f"\n2 Google News(闲鱼热门): {len(feed.entries)} 条")
    for e in feed.entries[:3]:
        print(f"   - {e.title[:50]}")
except: print("   ❌ 失败")

# 3. 百度热搜 API (模拟)
print("\n3 尝试其他数据源...")
# 试试爬虫方式获取 tophub 的抖音数据
try:
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    r = requests.get("https://tophub.today/c/douyin", headers=headers, timeout=10)
    if r.status_code == 200:
        # 提取标题类内容
        titles = re.findall(r'<a[^>]*href="/n/[^"]*"[^>]*>(.*?)</a>', r.text)
        print(f"   tophub.today(抖音): 找到 {len(titles)} 条", titles[:3] if titles else "")
    else:
        print(f"   tophub.today: HTTP {r.status_code}")
except Exception as e:
    print(f"   tophub.today: {str(e)[:40]}")

# 4. 换个源 - 微博热搜的抖音相关
try:
    r = requests.get("https://m.weibo.cn/api/container/getIndex?type=wb&queryVal=抖音", headers=headers, timeout=10)
    print(f"   微博API(抖音): {r.status_code}")
except Exception as e:
    print(f"   微博API: {str(e)[:30]}")

# 5. 尝试喜马拉雅热榜聚合
try:
    r = requests.get("https://www.163.com/dy/media/T1348647853363.html", headers=headers, timeout=10)
    if r.status_code == 200:
        print(f"   网易(抖音热门): HTTP 200 ({len(r.text)} bytes)")
    else:
        print(f"   网易(抖音热门): HTTP {r.status_code}")
except Exception as e:
    print(f"   网易: {str(e)[:30]}")
