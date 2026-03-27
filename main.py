import requests
from bs4 import BeautifulSoup
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import pytz
import os

def get_follow_list():
    """从 config.txt 读取你关注的球星名单"""
    if os.path.exists('config.txt'):
        with open('config.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    return ["辛纳", "高芙", "石宇奇"] # 如果没读到，默认关注这几位

def create_calendar():
    followers = get_follow_list()
    cal = Calendar()
    cal.add('prodid', '-//Sports Calendar Auto//')
    cal.add('version', '2.0')
    
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # --- 模拟/爬虫抓取到的原始数据 ---
    # 以后咱们可以在这里接入真正的爬虫逻辑，目前先确保 27-28 号的赛程精准
    raw_data = [
        {"id": "m_2026_001", "summary": "🎾 1/4决赛：辛纳 (Sinner) vs 蒂亚福", "start": "20260327T010000"},
        {"id": "m_2026_002", "summary": "🎾 1/4决赛：高芙 (Gauff) vs 穆霍娃", "start": "20260327T030000"},
        {"id": "m_2026_003", "summary": "🎾 1/4决赛：兹维列夫 vs 塞伦多罗", "start": "20260327T070000"},
        {"id": "m_2026_004", "summary": "🎾 半决赛：萨巴伦卡 vs 莱巴金娜", "start": "20260327T083000"},
        {"id": "b_2026_001", "summary": "🏸 1/4决赛：石宇奇 vs 安赛龙", "start": "20260328T153000"},
        {"id": "m_2026_005", "summary": "🎾 决赛预测：阿尔卡拉斯 vs 辛纳", "start": "20260329T200000"},
    ]

    print(f"当前关注名单: {followers}")
    count = 0

    for match in raw_data:
        # 核心过滤：标题里包含名单中的名字才加入日历
        if any(star in match['summary'] for star in followers):
            event = Event()
            event.add('summary', match['summary'])
            event.add('uid', match['id']) # 唯一ID，防止重复
            
            # 时间转换
            naive_start = datetime.strptime(match['start'], '%Y%m%dT%H%M%S')
            start_time = beijing_tz.localize(naive_start)
            
            event.add('dtstart', start_time)
            event.add('dtend', start_time + timedelta(hours=2)) # 默认占位2小时
            event.add('dtstamp', datetime.now(beijing_tz))
            
            cal.add_component(event)
            count += 1
            print(f"已添加: {match['summary']}")

    # 生成文件
    with open('my_schedule.ics', 'wb') as f:
        f.write(cal.to_ical())
    
    print(f"\n✅ 处理完成！共添加 {count} 场比赛到 my_schedule.ics")

if __name__ == "__main__":
    create_calendar()
