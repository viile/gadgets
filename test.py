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

def processAPP(lock,cur,uid):
    lock.acquire()
    try:
        for i in range(1,100):
            appid = 1000 + i
            cur.execute('insert into child_device_tb(uid,device_id,appid,time) values("'+str(uid)+'","pico-a9352800f54a52cb","'+str(appid)+'","'+str(todayStamp)+'")')
            print("uid : " + str(uid) + " appid: " + str(appid))
    finally:
        lock.release()

if __name__ == "__main__":
    conn = pymysql.connect(host='10.1.11.31',port=3306,user='dev',passwd='111111',charset='utf8',db='putao_children_server')
    cur = conn.cursor()
    for i in range(2001,10000):
        uid = 6100000 + i
        lock = multiprocessing.Lock()
        p = multiprocessing.Process(target = processAPP, args=(lock,cur,uid))
        p.start()
        p.join()

    conn.commit()
    cur.close()
    conn.commit()

