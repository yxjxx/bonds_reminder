# coding=utf-8
import json
import sys
import time
from datetime import timedelta

import requests
from ics import Calendar, DisplayAlarm, Event


def fetch_calendar_data(url, headers, retries=3, timeout=15):
    last_error = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            print("状态码：", response.status_code)
            response.raise_for_status()
            json_data = response.json()
            if not isinstance(json_data, list):
                raise ValueError("接口返回的 JSON 不是 list")
            return json_data
        except (requests.RequestException, json.JSONDecodeError, ValueError) as err:
            last_error = err
            print(f"[WARN] 第 {attempt}/{retries} 次请求失败: {err}")
            if attempt < retries:
                time.sleep(attempt)

    print(f"[ERROR] 获取接口数据失败，本次保留现有 kzz.ics 不更新: {last_error}")
    return None


def main():
    url = "https://www.jisilu.cn/data/calendar/get_calendar_data/?qtype=CNV"
    print(url)
    header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
    }
    json_data = fetch_calendar_data(url, header)
    if json_data is None:
        return 0

    bond_subscribe_data = []
    for data in json_data:
        try:
            item = {
                "id": data["id"],
                "code": data["code"],
                "title": data["title"],
                "start": data["start"],
                "description": data["description"],
                "url": data["url"],
                "color": data["color"],
            }
            bond_subscribe_data.append(item)
        except KeyError as err:
            print(f"[WARN] 跳过缺少字段的数据: {err}")

    start_bonds_data = []  # 待申购的可转债
    list_bonds_data = []  # 待上市的可转债
    for item in bond_subscribe_data:
        if "申购日" in item["title"]:
            start_bonds_data.append(item)
        if "上市日" in item["title"]:
            list_bonds_data.append(item)

    print('整理筛选后的申购数据:\n')
    c = Calendar()
    for d in list_bonds_data:
        listdate = d['start']  # 2022-04-25
        le = Event()
        le.name = d['title']
        ldate = listdate + " 00:00:00"  # '2022-04-25 00:00:00' 8:00
        le.begin = ldate.replace("00:00:00", "01:30:00")  # 9:30
        le.end = ldate.replace("00:00:00", "03:30:00")  # 9:30
        le.alarms.append(DisplayAlarm(trigger=timedelta(minutes=-5), display_text=le.name))
        le.alarms.append(DisplayAlarm(trigger=timedelta(seconds=-10), display_text=le.name))
        le.description = 'http://jisilu.cn/data/convert_bond_detail/%s' % (d['code'])
        c.events.add(le)

    for d in start_bonds_data:
        startdate = d['start']
        se = Event()
        se.name = d['title']
        sdate = startdate + " 00:00:00"  # '2022-04-25 00:00:00' 8:00
        se.begin = sdate.replace("00:00:00", "01:30:00")  # 9:30
        se.end = sdate.replace("00:00:00", "03:30:00")  # 11:30
        se.alarms.append(DisplayAlarm(trigger=timedelta(minutes=150), display_text=se.name))  # 12:00
        se.description = 'http://jisilu.cn/data/convert_bond_detail/%s' % (d['code'])
        c.events.add(se)

    with open('kzz.ics', 'w') as my_file:
        my_file.writelines(c)
        print('写入 kzz.ics:\n')

    return 0


if __name__ == '__main__':
    sys.exit(main())
