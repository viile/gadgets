#!/usr/bin/python  
# coding: utf-8

import re
import multiprocessing

def search(str,restr):
    lstr = len(str)
    index = 0
    r = []
    while index < lstr:
        result = re.search(restr,str[index:])
        if result :
            r.append(result)
            index += result.end()
        else :
            break

    return r

def processAPP(lock,linelist,relist):
    lock.acquire()
    try:
        result = map(search,linelist,relist)
        print(list(result))
    finally:
        lock.release()

if __name__ == "__main__":
    restr1 = '''((((ftp:|https:|http:)([\Q/\\E])*)|())(((%[0-9a-fA-F][0-9a-fA-F])|([a-zA-Z0-9])|([\Q$-_.+!*'(),;?&=\E]))+(:((%[0-9a-fA-F][0-9a-fA-F])|([a-zA-Z0-9])|([\Q$-_.+!*'(),;?&=\E]))*)?@)?(((((([a-zA-Z0-9]){1}([a-zA-Z0-9\-])*([a-zA-Z0-9]{1}))|([a-zA-Z0-9]))\.)+(biz|com|edu|gov|info|int|mil|name|net|org|pro|aero|cat|coop|jobs|museum|travel|arpa|root|mobi|post|tel|asia|geo|kid|mail|sco|web|xxx|nato|example|invalid|test|bitnet|csnet|onion|uucp|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cu|cv|cx|cy|cz|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|sk|sl|sm|sn|so|sr|st|su|sv|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|um|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw))|([0-9]{1,3}(\.[0-9]{1,3}){3}))(\:([0-9]+))?(([\Q/\\E])+((((%[0-9a-fA-F][0-9a-fA-F])|([a-zA-Z0-9])|([\Q$-_.+\!*'(),;:@&=\E]))*)(([\Q/\\E])*((%[0-9a-fA-F]{2})|([a-zA-Z0-9])|([\Q$-_.+\!*'(),;:@&=\E]))*)*)(\?((%[0-9a-fA-F]{2})|([a-zA-Z0-9])|([\Q$-_.+!*'(),;:@&=<>#"{}[] ^`~|\/\E]))*)*)*)'''
    restr2 = '''aaaaaaaaaaa'''
    restr3 = '''bbbbbbbbb'''
    relist = [restr1,restr2,restr3]

    with open('file', 'r') as file:
        while True:
            line = file.readline()
            if line :
                lock = multiprocessing.Lock()
                p = multiprocessing.Process(target = processAPP, args=(lock,[line]*len(relist),relist))
                p.start()
                p.join()
            else :
                break

