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
            return [line.strip() for line in f if line.strip()]
    return ["辛纳", "石宇奇"]

def fetch_live_data():
    params = {"key": TIAN_API_KEY, "num": 50}
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
    cal.add('prodid', '-//Sports Auto//')
    cal.add('version', '2.0')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    count = 0
    for item in news_list:
        content = item.get('title', '') + item.get('description', '')
        if any(star in content for star in followers):
            event = Event()
            event.add('summary', f"🏆 {item['title']}")
            try:
                pub_time = datetime.strptime(item['ctime'], '%Y-%m-%d %H:%M')
                start_time = beijing_tz.localize(pub_time)
                event.add('dtstart', start_time)
                event.add('dtend', start_time + timedelta(hours=1))
                event.add('uid', str(item['id']))
                cal.add_component(event)
                count += 1
            except: continue

    # 保底测试项：确保手机能看到
    test_event = Event()
    test_event.add('summary', '📖 自动化链路测试成功')
    test_event.add('dtstart', beijing_tz.localize(datetime(2026, 3, 28, 9, 0)))
    test_event.add('dtend', beijing_tz.localize(datetime(2026, 3, 28, 10, 0)))
    test_event.add('uid', 'test_success_001')
    cal.add_component(test_event)

    with open('my_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 完成！生成了 {count} 条赛程")

if __name__ == "__main__":
    create_calendar()
