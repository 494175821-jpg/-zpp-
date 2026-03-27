import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import os

TIAN_API_KEY = '211ed84f5ada94ad99a54addbafa7275' 
# 换成体育赛事专用接口
API_URL = "https://apis.tianapi.com/tiyu/index"

def get_follow_list():
    if os.path.exists('config.txt'):
        with open('config.txt', 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
    return ["梅德韦杰夫", "辛纳", "兹维列夫", "阿尔卡拉斯"]

def fetch_sports_data():
    # 直接抓取最新的 50 场体育赛事安排
    params = {"key": TIAN_API_KEY, "num": 50}
    try:
        res = requests.get(API_URL, params=params).json()
        if res.get("code") == 200:
            return res.get("result", {}).get("newslist", [])
    except: pass
    return []

def create_calendar():
    followers = get_follow_list()
    events_list = fetch_sports_data()
    cal = Calendar()
    cal.add('prodid', '-//Pro Sports Tracker//')
    cal.add('version', '2.0')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    count = 0
    for item in events_list:
        # 赛事接口通常包含 matchdate (日期) 和 matchtime (时间)
        title = item.get('title', '') # 比如 "迈阿密大师赛：梅德韦杰夫 VS 马查克"
        content = title.lower()
        
        # 只要标题里撞上你的名单，就抓！
        if any(star in content for star in followers):
            event = Event()
            event.add('summary', f"🎾 {title}")
            
            # 处理时间 (该接口返回通常是北京时间)
            try:
                # 尝试拼接日期和时间
                match_time_str = f"{item['matchdate']} {item['matchtime']}"
                dt = datetime.strptime(match_time_str, '%Y-%m-%d %H:%M')
                start_time = beijing_tz.localize(dt)
                
                event.add('dtstart', start_time)
                event.add('dtend', start_time + timedelta(hours=2))
                event.add('uid', f"match_{item.get('id', count)}")
                cal.add_component(event)
                count += 1
            except: continue

    # 状态栏更新
    status = Event()
    update_now = datetime.now(beijing_tz)
    status.add('summary', f"🔥 赛程库直连模式 | 发现 {count} 场焦点战")
    status.add('dtstart', update_now)
    status.add('dtend', update_now + timedelta(minutes=10))
    status.add('uid', f"status_{update_now.strftime('%Y%m%d%H%M')}")
    cal.add_component(status)

    with open('my_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 赛程库扫描完成，匹配到 {count} 场")

if __name__ == "__main__":
    create_calendar()
