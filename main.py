import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import os

# --- 配置区 ---
TIAN_API_KEY = '211ed84f5ada94ad99a54addbafa7275' 
NEWS_URL = "https://apis.tianapi.com/tiyunews/index"

def get_follow_list():
    # 自动包含一些“未来赛程”的触发词
    base_list = ["赛程", "预告", "对阵", "迈阿密", "全英赛", "半决赛", "决赛"]
    if os.path.exists('config.txt'):
        with open('config.txt', 'r', encoding='utf-8') as f:
            user_list = [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
            return list(set(base_list + user_list))
    return base_list

def fetch_data():
    # 抓取最近 150 条，尽量往回追溯，寻找包含未来时间的预告新闻
    params = {"key": TIAN_API_KEY, "num": 150}
    try:
        res = requests.get(NEWS_URL, params=params).json()
        return res.get("result", {}).get("newslist", []) if res.get("code") == 200 else []
    except: return []

def create_calendar():
    followers = get_follow_list()
    news_list = fetch_data()
    cal = Calendar()
    cal.add('prodid', '-//Future Sports//')
    cal.add('version', '2.0')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    seen_ids = set()
    count = 0

    for item in news_list:
        title = item.get('title', '')
        desc = item.get('description', '')
        content = (title + desc).lower()
        
        # 只要包含名单里的人，或者包含“赛程”类词汇
        if any(word in content for word in followers):
            news_id = item.get('id')
            if news_id in seen_ids: continue
            
            event = Event()
            event.add('summary', f"🏁 {title}")
            event.add('description', f"详情: {desc}\n发布时间: {item['ctime']}")
            
            try:
                # 注意：新闻快讯的时间是发布时间。
                # 既然是抓预告，我们将时间设为发布时间之后，方便你在日历中看到它。
                pub_time = datetime.strptime(item['ctime'], '%Y-%m-%d %H:%M')
                start_time = beijing_tz.localize(pub_time)
                event.add('dtstart', start_time)
                event.add('dtend', start_time + timedelta(hours=1))
                event.add('uid', str(news_id))
                
                cal.add_component(event)
                seen_ids.add(news_id)
                count += 1
            except: continue

    # 状态标记
    status = Event()
    status.add('summary', f"📅 近期赛程扫描中 (已发现 {count} 条相关)")
    status.add('dtstart', datetime.now(beijing_tz))
    status.add('dtend', datetime.now(beijing_tz) + timedelta(minutes=30))
    cal.add_component(status)

    with open('my_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 扫描完成，匹配到 {count} 条动态")

if __name__ == "__main__":
    create_calendar()
