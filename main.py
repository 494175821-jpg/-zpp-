import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import os

TIAN_API_KEY = '211ed84f5ada94ad99a54addbafa7275' 
# 换成这个支持搜索的接口地址
SEARCH_URL = "https://apis.tianapi.com/tiyunews/index"

def fetch_data(keyword):
    """根据关键词主动搜索新闻"""
    params = {"key": TIAN_API_KEY, "num": 10, "word": keyword}
    try:
        res = requests.get(SEARCH_URL, params=params).json()
        return res.get("result", {}).get("newslist", []) if res.get("code") == 200 else []
    except: return []

def create_calendar():
    # 我们选出三个最容易出新闻的词进行“深度探测”
    search_keywords = ["网球", "羽毛球", "中国"]
    
    cal = Calendar()
    cal.add('prodid', '-//Super Search Calendar//')
    cal.add('version', '2.0')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    seen_ids = set()
    count = 0

    for word in search_keywords:
        news_list = fetch_data(word)
        for item in news_list:
            news_id = item.get('id')
            if news_id in seen_ids: continue
            
            event = Event()
            event.add('summary', f"🎾 {item['title']}")
            event.add('description', item.get('description', ''))
            
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

    # 状态条：显示雷达最后探测的时间
    status = Event()
    status.add('summary', f"📡 深度扫描: 发现 {count} 条相关赛程")
    status.add('dtstart', datetime.now(beijing_tz))
    status.add('dtend', datetime.now(beijing_tz) + timedelta(minutes=10))
    cal.add_component(status)

    with open('my_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 主动搜索完成，抓取到 {count} 条动态")

if __name__ == "__main__":
    create_calendar()
