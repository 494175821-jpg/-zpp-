import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import os

TIAN_API_KEY = '211ed84f5ada94ad99a54addbafa7275' 
SEARCH_URL = "https://apis.tianapi.com/tiyunews/index"

def get_follow_list():
    if os.path.exists('config.txt'):
        with open('config.txt', 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
    return ["郑钦文", "辛纳", "梅德韦杰夫"]

def fetch_live_data():
    # 增加到 100 条，扩大搜索范围
    params = {"key": TIAN_API_KEY, "num": 100}
    try:
        response = requests.get(SEARCH_URL, params=params, timeout=10).json()
        if response.get("code") == 200:
            return response.get("result", {}).get("newslist", [])
    except: pass
    return []

def create_calendar():
    followers = get_follow_list()
    news_list = fetch_live_data()
    cal = Calendar()
    cal.add('prodid', '-//Global Sports Monitoring//')
    cal.add('version', '2.0')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    seen_ids = set()
    count = 0

    # 只要新闻里包含这些“强关联”词，就算匹配成功
    essential_keywords = ["迈阿密", "公开赛", "大师赛", "对阵", "晋级", "赛程"]

    for item in news_list:
        title = item.get('title', '')
        desc = item.get('description', '')
        content = (title + desc).lower()
        news_id = item.get('id')

        # 逻辑：(有人名) 或者 (迈阿密 + 关键球员名的一部分)
        match = any(star in content for star in followers)
        
        if match:
            if news_id in seen_ids: continue
            event = Event()
            event.add('summary', f"🏆 {title}")
            try:
                pub_time = datetime.strptime(item['ctime'], '%Y-%m-%d %H:%M')
                start_time = beijing_tz.localize(pub_time)
                event.add('dtstart', start_time)
                event.add('dtend', start_time + timedelta(hours=2))
                event.add('uid', str(news_id))
                cal.add_component(event)
                seen_ids.add(news_id)
                count += 1
            except: continue

    # 始终保留一个状态项，让你知道脚本跑过了
    status_event = Event()
    status_event.add('summary', f"📡 监控中: 匹配到 {count} 场比赛")
    now = datetime.now(beijing_tz)
    status_event.add('dtstart', now)
    status_event.add('dtend', now + timedelta(minutes=15))
    status_event.add('uid', f"status_{now.strftime('%Y%m%d%H%M')}")
    cal.add_component(status_event)

    with open('my_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 处理完毕，当前匹配数: {count}")

if __name__ == "__main__":
    create_calendar()
