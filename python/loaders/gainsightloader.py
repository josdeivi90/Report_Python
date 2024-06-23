import http.client
import json
import os
import datetime

from time import sleep
from collections import Counter

def load_new_users(year_number,month_number,keyMap):
    next_year = year_number
    next_month = (month_number+1)
    if month_number==12:
        next_month=1
        next_year=year_number+1
    
    conn = http.client.HTTPSConnection("api.aptrinsic.com")
    gpx_token = os.environ['GAINSIGHT_API_KEY']
    payload = ''
    headers = {
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
        'X-APTRINSIC-API-KEY': gpx_token
        }
    scrollId = ""
    hasData = True
    outputMap = []
    for service in keyMap:
        servMap = {
            "name" : service["name"],
            "production" : 0,
            "nonprod" : 0,
            "sandbox" : 0,
            "demo" : 0,
            "preprod" : 0
        }
        outputMap.append(servMap)
    while (hasData):
        retries = 6
        while retries>0:
            sleep(1)
            uri="/v1/users?pageSize=1000&filter=signUpDate%3E%3D"+str(date_to_epoch_ms(year_number,month_number,1))+";signUpDate%3C"+str(date_to_epoch_ms(next_year,next_month,1))+"&scrollId="+scrollId
            conn.request("GET", uri, payload, headers)
            res=conn.getresponse()
            data=json.loads(res.read())
            if "users" in data:
                retries = 0
            else:
                sleep(5)
                print ("Retrying")
                retries -= 1
        users=data["users"]
        scrollId=data["scrollId"]
        if len(users) > 0:
            for user in users:
                keys = user["propertyKeys"]
                for key in keys:
                    for service in keyMap:
                        if key==service["production"]:
                            for outServ in outputMap:
                                if outServ["name"]==service["name"]:
                                    outServ["production"] += 1
                        elif key==service["nonprod"]:
                            for outServ in outputMap:
                                if outServ["name"]==service["name"]:
                                    outServ["nonprod"] += 1
                        elif key==service["sandbox"]:
                            for outServ in outputMap:
                                if outServ["name"]==service["name"]:
                                    outServ["sandbox"] += 1
                        elif key==service["demo"]:
                            for outServ in outputMap:
                                if outServ["name"]==service["name"]:
                                    outServ["demo"] += 1
                        elif key==service["preprod"]:
                            for outServ in outputMap:
                                if outServ["name"]==service["name"]:
                                    outServ["preprod"] += 1
        else:
            hasData=False
    return outputMap

def load_unique_users(year_number, month_number, keyMap):
    conn=http.client.HTTPSConnection("api.aptrinsic.com")
    gpx_token=os.environ['GAINSIGHT_API_KEY']
    payload=''
    headers={
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
        'X-APTRINSIC-API-KEY': gpx_token
        }
    next_year = year_number
    next_month = (month_number+1)
    if month_number==12:
        next_month=1
        next_year=year_number+1
    scrollId = ""
    hasData = True
    listMap = []
    for service in keyMap:
        servMap = {
            "name" : service["name"],
            "prodList" : [],
            "devList" : [],
            "sandList" : [],
            "demoList" : [],
            "preprodList" : []
        }
        listMap.append(servMap)
    templist = []
    while (hasData):
        retries = 6
        while retries>0:
            sleep(1)
            uri="/v1/events/session?pageSize=1000&filter=date%3E%3D"+str(date_to_epoch_ms(year_number,month_number,1))+";date%3C"+str(date_to_epoch_ms(next_year,next_month,1))+";userType==USER"
            if scrollId:
                uri=uri+"&scrollId="+scrollId
            conn.request("GET", uri, payload, headers)
            res=conn.getresponse()
            data=json.loads(res.read())
            if "sessionInitializedEvents" in data:
                retries = 0
            else:
                sleep(3)
                print ("Retrying")
                retries -= 1
        sessions=data["sessionInitializedEvents"]
        scrollId=data["scrollId"]
        if len(sessions) > 0:
            for session in sessions:
                key = session["propertyKey"]
                for service in keyMap:
                    if key==service["production"]:
                        for outServ in listMap:
                            if outServ["name"]==service["name"]:
                                outServ["prodList"].append(session["identifyId"])
                    elif key==service["nonprod"]:
                        for outServ in listMap:
                            if outServ["name"]==service["name"]:
                                outServ["devList"].append(session["identifyId"])
                    elif key==service["sandbox"]:
                        for outServ in listMap:
                            if outServ["name"]==service["name"]:
                                outServ["sandList"].append(session["identifyId"])
                    elif key==service["demo"]:
                        for outServ in listMap:
                            if outServ["name"]==service["name"]:
                                outServ["demoList"].append(session["identifyId"])
        else:
            hasData=False
        if scrollId is None:
            hasData=False
    outputMap = []
    for service in listMap:
        servMap = {
            "name" : service["name"],
            "production" : len(Counter(service["prodList"]).keys()),
            "nonprod" : len(Counter(service["devList"]).keys()),
            "sandbox" : len(Counter(service["sandList"]).keys()),
            "demo" : len(Counter(service["demoList"]).keys()),
            "preprod" : len(Counter(service["demoList"]).keys()) #preprod is the same as demo
        }
        outputMap.append(servMap)
    return outputMap

def load_sessions(year_number, month_number, keyMap, userType):
    conn=http.client.HTTPSConnection("api.aptrinsic.com")
    gpx_token=os.environ['GAINSIGHT_API_KEY']
    payload=''
    headers={
        'X-Requested-With': 'XMLHttpRequest',
        'Content-Type': 'application/json',
        'X-APTRINSIC-API-KEY': gpx_token
        }
    next_year = year_number
    next_month = (month_number+1)
    if month_number==12:
        next_month=1
        next_year=year_number+1
    outputMap = []
    for service in keyMap:
        baseuri="/v1/events/session?filter=date%3E%3D"+str(date_to_epoch_ms(year_number,month_number,1))+";date%3C"+str(date_to_epoch_ms(next_year,next_month,1))+";userType=="+userType+";"
        uri = baseuri+"sessionId~"+service["production"]+"*"
        conn.request("GET", uri, payload, headers)
        res=conn.getresponse()
        data=json.loads(res.read())
        prodSessions = data["totalHits"]
        sleep(1)
        uri = baseuri+"sessionId~"+service["nonprod"]+"*"
        conn.request("GET", uri, payload, headers)
        res=conn.getresponse()
        data=json.loads(res.read())
        nonprodSessions = data["totalHits"]
        sleep(1)
        uri = baseuri+"sessionId~"+service["sandbox"]+"*"
        conn.request("GET", uri, payload, headers)
        res=conn.getresponse()
        data=json.loads(res.read())
        sandboxSessions = data["totalHits"]
        sleep(1)
        uri = baseuri+"sessionId~"+service["demo"]+"*"
        conn.request("GET", uri, payload, headers)
        res=conn.getresponse()
        data=json.loads(res.read())
        demoSessions = data["totalHits"]
        preprodSessions = demoSessions
        servMap = {
            "name" : service["name"],
            "production" : prodSessions,
            "nonprod" : nonprodSessions,
            "sandbox" : sandboxSessions,
            "demo" : demoSessions,
            "preprod" : preprodSessions
        }
        outputMap.append(servMap)
    return outputMap

def load_user_sessions(year_number, month_number, keyMap):
    return load_sessions(year_number, month_number, keyMap, "USER")

def load_all_sessions(year_number, month_number, keyMap):
    return load_sessions(year_number, month_number, keyMap, "")

def date_to_epoch_ms(year, month, day):
    num=(datetime.datetime(year,month,day,0,0) - datetime.datetime(1970,1,1)).total_seconds()
    return int(num*1000)

#temporary main used for generating historical data from local only
def main(): 
    MONTH = 11
    YEAR = 2023
    
    with open("./config/config.json") as f:
        config = json.load(f)
    print("Metric\tMonth\tService\tProduction\tNonProd\tSandbox\tPreProd\tDemo")
    while (MONTH < 5 or YEAR < 2024):
        user_sessions = load_user_sessions(YEAR,MONTH,config['gs_property_keys'])
        all_sessions = load_all_sessions(YEAR,MONTH,config['gs_property_keys'])
        new_users = load_new_users(YEAR,MONTH,config['gs_property_keys'])
        active_users = load_unique_users(YEAR,MONTH,config['gs_property_keys'])
        data = {
                'user_sessions' : user_sessions,
                'all_sessions' : all_sessions,
                'new_users' : new_users,
                'active_users' : active_users
            }
        for service in data["user_sessions"]:
           print ("user_sessions"+"\t"+str(MONTH)+"/"+str(YEAR)+"\t"+service["name"]+"\t"+str(service["production"])+"\t"+str(service["nonprod"])+"\t"+str(service["sandbox"])+"\t"+str(service["preprod"])+"\t"+str(service["demo"]))
        for service in data["all_sessions"]:
           print ("all_sessions"+"\t"+str(MONTH)+"/"+str(YEAR)+"\t"+service["name"]+"\t"+str(service["production"])+"\t"+str(service["nonprod"])+"\t"+str(service["sandbox"])+"\t"+str(service["preprod"])+"\t"+str(service["demo"]))
        for service in data["new_users"]:
           print ("new_users"+"\t"+str(MONTH)+"/"+str(YEAR)+"\t"+service["name"]+"\t"+str(service["production"])+"\t"+str(service["nonprod"])+"\t"+str(service["sandbox"])+"\t"+str(service["preprod"])+"\t"+str(service["demo"]))
        for service in data["active_users"]:
           print ("active_users"+"\t"+str(MONTH)+"/"+str(YEAR)+"\t"+service["name"]+"\t"+str(service["production"])+"\t"+str(service["nonprod"])+"\t"+str(service["sandbox"])+"\t"+str(service["preprod"])+"\t"+str(service["demo"]))
        if (MONTH==12):
            MONTH=1
            YEAR+=1
        else:
            MONTH+=1
if __name__ == "__main__":
    main()
