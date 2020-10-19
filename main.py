# coding=utf-8
import requests
import json
from datetime import datetime, timedelta
from ics import Calendar, Event, DisplayAlarm

def main():
    url = "http://dcfm.eastmoney.com/em_mutisvcexpandinterface/api/js/get?type=KZZ_LB2.0&token=70f12f2f4f091e459a279469fe49eca5&p=1&st=STARTDATE&sr=-1&ps=50"
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

    subscribe_json_data = [] # 所有还未上市的可转债
    for data in json_data:
        now_date = datetime.now().date()        
        LISTDATE = data['LISTDATE'].split('T')[0] 
        if LISTDATE == '-': 
            LISTDATE = now_date
        else:
            LISTDATE = datetime.strptime(LISTDATE, '%Y-%m-%d').date()
                
        if LISTDATE < now_date:
            # print("可转债信息过期！")
            continue
        subscribe_json_data.append(data)

    bond_subscribe_data = []
    for data in subscribe_json_data:
        dict = {}
        try:
            dict['STARTDATE'] = data['STARTDATE']  # 申购日期
            dict['LISTDATE'] = data['LISTDATE']  # 上市日期 可能为 -
            dict['BONDCODE'] = data['BONDCODE']  # 债券代码
            dict['SNAME'] = data['SNAME']  # 债券简称
            dict['CORRESCODE'] = data['CORRESCODE']  # 申购代码
            dict['ZGJ'] = data['ZGJ']  # 正股价
            dict['SWAPPRICE'] = data['SWAPPRICE']  # 转股价
            dict['ZGPRICE'] = (100 * float(dict['ZGJ'])) / float(dict['SWAPPRICE'])  # 转股价值
            # 债现价
            # 转股溢价率
            bond_subscribe_data.append(dict)
        except Exception as err:
            print(err)

    print('整理筛选后的申购数据:\n')
    c = Calendar()
    for d in bond_subscribe_data:
        listdate = d['LISTDATE'] #2020-10-21T00:00:00       
        if listdate != '-':
            le = Event()
            le.name = d['SNAME'] +"上市"
            le.begin = listdate.replace("T"," ") #'2014-01-01 00:00:00'
            le.alarms.append(DisplayAlarm(trigger=timedelta(minutes=85), display_text=le.name))
            c.events.add(le)

        startdate = d['STARTDATE']
        if startdate != '-':
            se = Event()
            se.name = d['SNAME'] +"申购"
            se.begin = startdate.replace("T"," ") #'2014-01-01 00:00:00'            
            se.alarms.append(DisplayAlarm(trigger=timedelta(minutes=90), display_text=se.name))
            c.events.add(se)
        
        # [<Event 'My cool event' begin:2014-01-01 00:00:00 end:2014-01-01 00:00:01>]
        with open('kzz.ics', 'w') as my_file:
            my_file.writelines(c)
if __name__ == '__main__':
    main()