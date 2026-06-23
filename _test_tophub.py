import requests, re, json
from bs4 import BeautifulSoup

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}

print("=== 解析 tophub.today 找到抖音热榜数据 ===\n")

r = requests.get("https://tophub.today/", headers=headers, timeout=10)
soup = BeautifulSoup(r.text, "html.parser")

# 找到所有板块
all_panels = soup.select("div.cc-panel")
print(f"共找到 {len(all_panels)} 个板块\n")

for panel in all_panels:
    title_el = panel.select_one("div.cc-panel-head span")
    title = title_el.get_text(strip=True) if title_el else "未知"
    
    items = panel.select("div.cc-cd-c")
    if "抖音" in title or "抖" in title:
        print(f"🎯 找到抖音板块: {title}")
        for item in items[:10]:
            a = item.select_one("a")
            t = a.get_text(strip=True) if a else ""
            print(f"   - {t[:50]}")
        print()
    elif "闲鱼" in title or "咸鱼" in title:
        print(f"🎯 找到闲鱼板块: {title}")
        for item in items[:10]:
            a = item.select_one("a")
            t = a.get_text(strip=True) if a else ""
            print(f"   - {t[:50]}")
        print()

# 看看都有哪些板块
print("=== 所有板块名称 ===")
for panel in all_panels[:30]:
    title_el = panel.select_one("div.cc-panel-head span")
    title = title_el.get_text(strip=True) if title_el else "未知"
    items = panel.select("div.cc-cd-c")
    print(f"  {title}: {len(items)} 条")
