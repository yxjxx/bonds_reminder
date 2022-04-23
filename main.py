# coding=utf-8
import json
from datetime import datetime, timedelta

import requests
from ics import Calendar, DisplayAlarm, Event


def main():
    url = "https://www.jisilu.cn/data/calendar/get_calendar_data/?qtype=CNV"
    print(url)
    try:
        header = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"
        }
        response = requests.get(url, headers=header)
        status_code = response.status_code
        print("状态码：", status_code)
        response.encoding = response.apparent_encoding
        json_data = json.loads(response.text)
        
    except Exception as err:
        print(err)

    bond_subscribe_data = []
    for data in json_data:
        dict = {}
        try:
            dict['id'] = data['id']
            dict['code'] = data['code']
            dict['title'] = data['title']
            dict['start'] = data['start']
            dict['description'] = data['description']
            dict['url'] = data['url']
            dict['color'] = data['color']
            bond_subscribe_data.append(dict)
        except Exception as err:
            print(err)

    start_bonds_data = [] #待申购的可转债
    list_bonds_data = [] # 待上市的可转债    
    for dict in bond_subscribe_data:
        if "申购日" in dict['title']:
            start_bonds_data.append(dict)
        if "上市日" in dict['title']:
            list_bonds_data.append(dict)

    print('整理筛选后的申购数据:\n')
    c = Calendar()
    for d in list_bonds_data:
        listdate = d['start'] #2022-04-25
        le = Event()
        le.name = d['title']
        ldate = listdate + " 00:00:00" #'2022-04-25 00:00:00' 8:00
        le.begin = ldate.replace("00:00:00", "01:30:00") # 9:30
        le.end = ldate.replace("00:00:00", "03:30:00") # 9:30
        le.alarms.append(DisplayAlarm(trigger=timedelta(minutes=-5), display_text=le.name))
        le.alarms.append(DisplayAlarm(trigger=timedelta(seconds=-10), display_text=le.name))
        le.description = 'http://jisilu.cn/data/convert_bond_detail/%s' % (d['code'])
        c.events.add(le)

    for d in start_bonds_data:
        startdate = d['start']
        se = Event()
        se.name = d['title']
        sdate = startdate + " 00:00:00" #'2022-04-25 00:00:00' 8:00
        se.begin = sdate.replace("00:00:00", "01:30:00") # 9:30
        se.end = sdate.replace("00:00:00", "03:30:00")  # 11:30
        se.alarms.append(DisplayAlarm(trigger=timedelta(minutes=150), display_text=se.name))# 12:00
        se.description = 'http://jisilu.cn/data/convert_bond_detail/%s' % (d['code'])
        c.events.add(se)
        
    with open('kzz.ics', 'w') as my_file:
        my_file.writelines(c)
        print('写入 kzz.ics:\n')
        
if __name__ == '__main__':
    main()
