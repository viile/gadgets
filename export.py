import os
import re
import sys
import csv
import time
import MySQLdb
import datetime
import commands
import shutil
import string
import ConfigParser
import multiprocessing

def getDataFormDB(host,user,passwd,db,port,t,lock,result):
    conn = MySQLdb.connect(host=host,user=user,passwd=passwd,db=db,port=port)
    cur=conn.cursor()
    cur.execute('select calleee164 from e_cdr_%s where endreason = -7 or stoptime > starttime group by calleee164;' %t)
    if cur:
        return exportDataToFile(cur.fetchall(),lock,result)
    else:
        print(host + " db connect error")
        return 0

def exportDataToFile(data,lock,filename):
    lock.acquire()
    try:
       r = open(filename, 'a+')
       for phone in data:
           r.write(phone[0] + "\r\n")
    finally:
        lock.release()
    return 0

def getConfig(filename):
    cf = ConfigParser.ConfigParser()
    cf.read(filename)
    hostlist = []
    for host in cf.sections():
        hostlist.append([cf.get(host,"host"),cf.get(host,"database"),cf.getint(host,"port"),cf.get(host,"username"),cf.get(host,"password")])
    return hostlist

if __name__ == "__main__":
    config = getConfig('host.conf')
    t = time.strftime('%Y%m%d',time.localtime(time.time()))
    result = "cdr_" + t
    for c in config:
        host = c[0]
        db = c[1]
        port = c[2]
        user = c[3]
        passwd = c[4]
        if host and db and port and user and passwd:
            lock = multiprocessing.Lock()
            p = multiprocessing.Process(target = getDataFormDB, args=(host,user,passwd,db,port,t,lock, result))
            p.start()
            print(host + " is end")
        else:
            print("config error")


