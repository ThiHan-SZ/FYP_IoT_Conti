import time
from datetime import datetime, timedelta
import pytz


def getTimeStampInMs():
    tz = pytz.timezone('Asia/Shanghai')
    t = datetime.now(tz).timestamp()
    nowTime = int(round(t * 1000))
    return str(nowTime)


def getDateString4title():
    tz = pytz.timezone('Asia/Shanghai')
    t = datetime.now(tz)
    return t.strftime('%Y_%m_%d_%H#%M#%S')

def getDateString():
    tz = pytz.timezone('Asia/Shanghai')
    t = datetime.now(tz)
    return t.strftime('%Y/%m/%d %H:%M:%S')

def milliSleep(milli):
    time.sleep(milli / 1000)


def isTimeOut(stamp1, interval):
    result = False
    stamp_Now = getTimeStampInMs()
    # print(stamp_Now,stamp1,int(stamp_Now) - int(stamp1))
    if int(stamp_Now) - int(stamp1) > interval:
        result = True
    return result

def getDateOnlyString():
    tz = pytz.timezone('Asia/Shanghai')
    t = datetime.now(tz)
    return t.strftime('%Y_%m_%d')

def getTimeOnlyString():
    tz = pytz.timezone('Asia/Shanghai')
    t = datetime.now(tz)
    return t.strftime('%H:%M:%S')

