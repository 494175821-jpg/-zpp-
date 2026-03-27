import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import os

# --- 配置区 ---
TIAN_API_KEY = '211ed84f5ada94ad99a54addbafa7275' 
SEARCH_URL = "https://apis.tianapi.com/tiyunews/index"

def get_follow_list():
    if os.path.exists('config.txt'):
        with open('config.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return ["辛纳", "石宇奇"]

def fetch_live_data():
    params = {"key": TIAN_API_KEY, "num": 50}
    try:
        response = requests.get(SEARCH_URL, params=params, timeout=10).json()
        if response.get("code") == 200:
            return response.get("result", {}).get("newslist", [])
    except:
        pass
    return []

def create_calendar():
    followers = get_follow_list()
    news_list = fetch_live_data()
    cal = Calendar()
    cal.add('prodid', '-//Sports Auto//')
    cal.add('version', '2.0')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    count = 0
    # --- 逻辑 A: 自动抓取 ---
    for item in news_list:
        content = item.get('title', '') + item.get('description', '')
        if any(star in content for star in followers):
            event = Event()
            event.add('summary', f"🎾 {item['title']}")
            try:
                pub_time = datetime.strptime(item['ctime'], '%Y-%m-%d %H:%M')
                start_time = beijing_tz.localize(pub_time)
                event.add('dtstart', start_time)
                event.add('dtend', start_time + timedelta(hours=2))
                event.add('uid', str(item['id']))
                cal.add_component(event)
                count += 1
            except: continue

    # --- 逻辑 B: 保底测试数据 (确保你手机现在能看到东西) ---
    # 如果你想确认订阅是否成功，这里强行加一个明天的测试日程
    test_event = Event()
    test_event.add('summary', '🚀 自动更新测试: 辛纳/石宇奇待定比赛')
    test_event.add('dtstart', beijing_tz.localize(datetime(2026, 3, 27, 20, 0))) # 明晚8点
    test_event.add('dtend', beijing_tz.localize(datetime(2026, 3, 27, 22, 0)))
    test_event.add('uid', 'test_20260327_001')
    cal.add_component(test_event)

    with open('my_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 完成！抓取到 {count} 条相关赛程，并添加了测试项")

if __name__ == "__main__":
    create_calendar()
