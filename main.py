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
            # 过滤注释和空行，统一转小写
            return [line.strip().lower() for line in f if line.strip() and not line.startswith('#')]
    return ["郑钦文", "辛纳", "石宇奇"]

def fetch_live_data():
    """从 API 抓取体育快讯"""
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
    cal.add('prodid', '-//Sports Stars Calendar//')
    cal.add('version', '2.0')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    seen_ids = set()
    count = 0

    for item in news_list:
        title = item.get('title', '')
        desc = item.get('description', '')
        content = (title + desc).lower()
        news_id = item.get('id')

        # 匹配逻辑：名单中任何一个人出现在新闻中
        if any(star in content for star in followers):
            if news_id in seen_ids: continue
            
            event = Event()
            event.add('summary', f"🏆 {title}")
            event.add('description', f"{desc}\n来源: {item.get('source', '体育快讯')}")
            
            try:
                # 转换发布时间
                pub_time = datetime.strptime(item['ctime'], '%Y-%m-%d %H:%M')
                start_time = beijing_tz.localize(pub_time)
                
                event.add('dtstart', start_time)
                event.add('dtend', start_time + timedelta(hours=2))
                event.add('uid', str(news_id))
                event.add('dtstamp', datetime.now(beijing_tz))
                
                cal.add_component(event)
                seen_ids.add(news_id)
                count += 1
            except: continue

    # 始终保留一个更新成功的小提醒（可选，如果不需要可以删掉下面这几行）
    update_note = Event()
    update_note.add('summary', f"✅ 赛程库已更新 (匹配到{count}项)")
    update_note.add('dtstart', datetime.now(beijing_tz))
    update_note.add('dtend', datetime.now(beijing_tz) + timedelta(minutes=10))
    update_note.add('uid', 'update_status_' + datetime.now().strftime('%Y%m%d%H'))
    cal.add_component(update_note)

    with open('my_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 全量监控已开启，匹配到 {count} 条顶级球员动态")

if __name__ == "__main__":
    create_calendar()
