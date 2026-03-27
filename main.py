import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import os

TIAN_API_KEY = '211ed84f5ada94ad99a54addbafa7275' 
API_URL = "https://apis.tianapi.com/tiyunews/index"

def fetch_data():
    # 扩大搜索到 150 条，不设关键词，抓取所有最新的体育新闻
    params = {"key": TIAN_API_KEY, "num": 150}
    try:
        res = requests.get(API_URL, params=params).json()
        return res.get("result", {}).get("newslist", []) if res.get("code") == 200 else []
    except: return []

def create_calendar():
    # 只要新闻里有这些词，就强制塞进日历，不怕多，就怕没！
    force_keywords = ["梅德韦杰夫", "辛纳", "迈阿密", "网球", "兹维列夫", "大师赛", "对阵"]
    
    news_list = fetch_data()
    cal = Calendar()
    cal.add('prodid', '-//Ultimate Tracker//')
    cal.add('version', '2.0')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    seen_ids = set()
    count = 0

    for item in news_list:
        title = item.get('title', '')
        desc = item.get('description', '')
        content = (title + desc).lower()
        
        # 只要命中了任何一个关键词
        if any(word in content for word in force_keywords):
            news_id = item.get('id')
            if news_id in seen_ids: continue
            
            event = Event()
            event.add('summary', f"🎾 {title}")
            event.add('description', f"详情: {desc}")
            
            try:
                pub_time = datetime.strptime(item['ctime'], '%Y-%m-%d %H:%M')
                start_time = beijing_tz.localize(pub_time)
                event.add('dtstart', start_time)
                event.add('dtend', start_time + timedelta(hours=1))
                event.add('uid', str(news_id))
                cal.add_component(event)
                seen_ids.add(news_id)
                count += 1
            except: continue

    # 状态条：让你知道它确实在拼命工作
    status = Event()
    now_str = datetime.now(beijing_tz).strftime('%H:%M:%S')
    status.add('summary', f"🚀 深度扫描已完成 | 捕获 {count} 条相关消息")
    status.add('dtstart', datetime.now(beijing_tz))
    status.add('dtend', datetime.now(beijing_tz) + timedelta(minutes=10))
    cal.add_component(status)

    with open('my_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 扫描完成，匹配数: {count}")

if __name__ == "__main__":
    create_calendar()
