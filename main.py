import requests
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import os

# --- 配置区 ---
# 请去 tianapi.com 注册后替换这个 KEY（每天有免费额度）
TIAN_API_KEY = '211ed84f5ada94ad99a54addbafa7275' 
SEARCH_URL = "https://apis.tianapi.com/tiyunews/index"

def get_follow_list():
    if os.path.exists('config.txt'):
        with open('config.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return ["辛纳", "石宇奇"]

def fetch_live_data():
    """从 API 实时抓取体育赛程快讯"""
    params = {
        "key": TIAN_API_KEY,
        "num": 50  # 抓取最近 50 条体育动态
    }
    try:
        response = requests.get(SEARCH_URL, params=params).json()
        if response.get("code") == 200:
            return response["result"]["newslist"]
    except Exception as e:
        print(f"抓取失败: {e}")
    return []

def create_calendar():
    followers = get_follow_list()
    news_list = fetch_live_data()
    cal = Calendar()
    cal.add('prodid', '-//Auto Sports Calendar//')
    cal.add('version', '2.0')
    beijing_tz = pytz.timezone('Asia/Shanghai')

    count = 0
    for item in news_list:
        content = item['title'] + item['description']
        # 核心逻辑：只要新闻标题或内容里包含你名单里的球员
        if any(star in content for star in followers):
            event = Event()
            event.add('summary', f"🏆 赛程动态: {item['title']}")
            event.add('description', item['description'] + "\n来源: " + item['source'])
            
            # 由于快讯通常是实时预报，我们假设比赛在快讯发布后的 2 小时内
            # 这是一个初级逻辑，后续我们可以接入更精准的 Score API
            pub_time = datetime.strptime(item['ctime'], '%Y-%m-%d %H:%M')
            start_time = beijing_tz.localize(pub_time)
            
            event.add('dtstart', start_time)
            event.add('dtend', start_time + timedelta(hours=2))
            event.add('uid', item['id'])
            
            cal.add_component(event)
            count += 1
            print(f"匹配到赛程: {item['title']}")

    with open('my_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())
    print(f"✅ 全自动同步完成，共抓取到 {count} 条相关赛程")

if __name__ == "__main__":
    create_calendar()
