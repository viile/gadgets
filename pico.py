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

def processKey(lock,ncur,key):
    lock.acquire()
    try:
        ncur.execute('insert into children_key_tb(appid,secret_key,description) values("'+str(key[1])+'","'+str(key[2])+'","'+str(key[3])+'")')
    finally:
        lock.release()

def processUser(lock,ncur,user):
    lock.acquire()
    try:
        ncur.execute('insert into children_tb(nickname,uid,passwd_status,device_id,birthday,account_name,gender) values("'+user[1]+'","'+str(user[3])+'","1","","1473317357","'+user[8]+'","1")')
    finally:
        lock.release()

if __name__ == "__main__":
    conn = pymysql.connect(host='10.1.11.31',port=3306,user='dev',passwd='111111',charset='utf8',db='pico')
    cur = conn.cursor()
    nconn = pymysql.connect(host='10.1.11.31',port=3306,user='dev',passwd='111111',charset='utf8',db='putao_children_server')
    ncur = nconn.cursor()
    cur.execute('select * from api_user_key')
    keyList = cur.fetchall()
    cur.execute('select * from pico_user')
    userList = cur.fetchall()
    for key in keyList:
        lock = multiprocessing.Lock()
        p = multiprocessing.Process(target = processKey, args=(lock,ncur,key))
        p.start()
        p.join()
    for user in userList:
        lock = multiprocessing.Lock()
        p = multiprocessing.Process(target = processUser, args=(lock,ncur,user))
        p.start()
        p.join()
    
    conn.commit()
    cur.close()
    conn.commit()
    nconn.commit()
    ncur.close()
    nconn.commit()


