#!/usr/bin/python  
# coding: utf-8

import time
import datetime
import json
import pymysql
import requests
import multiprocessing

URL = 'https://api.heweather.com/x3/weather'
KEY = '12ec06a309fd4d0bbb784728f5935fd7'
today = datetime.date.today()
todayStamp = int(time.mktime(datetime.date(today.year,today.month,today.day).timetuple()))

def processAPP(lock,cur,city):
    lock.acquire()
    try:
        res = requests.get(URL + '?cityid=' + city + '&key=' + KEY)
        if(res.status_code == 200):
            content = json.loads(res.text)
            if(content["HeWeather data service 3.0"][0]["status"] == "ok"):
                cur.execute('insert into weather(city,time,data) values("'+city+'","'+str(todayStamp)+'","'+str(content["HeWeather data service 3.0"][0])+'")')
                print(city + " successfully written")
            else:
                print(city + "json parsing error")
        else:
            print(city + "network error")
    finally:
        lock.release()

if __name__ == "__main__":
    conn = pymysql.connect(host='10.1.11.31',port=3306,user='dev',passwd='111111',charset='utf8',db='viiler_weather')
    cur = conn.cursor()
    cur.execute('select id from city')
    cityList = cur.fetchall()
    for city in cityList:
        lock = multiprocessing.Lock()
        p = multiprocessing.Process(target = processAPP, args=(lock,cur,city[0]))
        p.start()
        p.join()
    
    conn.commit()
    cur.close()
    conn.commit()

