import http.client
import json
import os
from utils.configuration import load_configuration
from utils.dateutils import days_in_month

def start_time(month, year):
    out = str(year).zfill(4)+"-"+str(month).zfill(2)
    return out


def end_time(month, year, day):
    out = str(year).zfill(4)+"-"+str(month).zfill(2)+"-" + \
        str(day).zfill(2)
    return out


def load_perspective_costs(token, cost_config, month, year, currentday=0):
    outdata=[]
    for perspective in cost_config["perspectives"]:
        total = 0
        trend = 0
        for id in perspective["ids"]:
            conn = http.client.HTTPSConnection("app.harness.io")
            payload = json.dumps({
                "filters": [],
                "groupBy": [],
                "skipRoundOff": False
            })
            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'x-api-key': token
            }
            if currentday>0:
                for_day = currentday
            else:
                for_day = days_in_month(month,year)
            uri = "/ccm/api/costdetails/overview?accountIdentifier="+cost_config["account_id"]+"&perspectiveId="+id+"&startTime=" + \
                start_time(month, year)+"&endTime="+end_time(month, year, for_day)
            retries = 0
            while (retries<3):
                try:
                    conn.request("POST", uri, payload, headers)
                    res = conn.getresponse()
                    data = json.loads(res.read())
                    if data["status"] == "SUCCESS":
                        break
                    else:
                        retries+=1
                except:
                    retries+=1
            total += data["data"]["value"]
            trend += data["data"]["statsTrend"]
        #now grab budget data
        for id in perspective["ids"]:
            conn = http.client.HTTPSConnection("app.harness.io")
            uri = "/gateway/ccm/api/budgets/perspectiveBudgets?accountIdentifier="+cost_config["account_id"]+"&perspectiveId="+id
            payload = ''
            retries = 0
            while (retries<3):
                try:
                    conn.request("GET", uri, payload, headers)
                    res = conn.getresponse()
                    data = json.loads(res.read())
                    if data["status"] == "SUCCESS":
                        break
                    else:
                        retries+=1
                except:
                    retries+=1
            forecast_pcts = 0
            if retries<3 and (len(data["data"])>0): 
                forecast_pcts += data["data"][0]["forecastCost"]/data["data"][0]["budgetAmount"]*100
            else: 
                print ("error fetching budget data for perspective "+perspective["name"]+" id "+id)

        forecast_pct_of_budget = round(forecast_pcts/len(perspective["ids"]),2)
        thisdata = {
            "application" : perspective["name"],
            "total" : round(total,2),
            "trend" : round(trend,2),
            "forecast_pct_of_budget" : forecast_pct_of_budget
            }
        outdata.append(thisdata)
    return outdata

def load_aws_account_cost(token, cost_config, aws_perspective_id, harness_account_id, month, year, currentday=0):
    outdata=[]
    conn = http.client.HTTPSConnection("app.harness.io")
    payload = json.dumps({
        "filters": [],
        "groupBy": ["AWS_ACCOUNT"],
        "skipRoundOff": False
    })
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'x-api-key': token
    }
    if currentday>0:
        for_day = currentday
    else:
        for_day = days_in_month(month,year)
    uri = "/ccm/api/costdetails/tabularformat?accountIdentifier="+harness_account_id+"&perspectiveId="+aws_perspective_id+"&startTime=" + \
        start_time(month, year)+"&endTime="+end_time(month, year, for_day)
    retries = 0
    while (retries<3):
        try:
            conn.request("POST", uri, payload, headers)
            res = conn.getresponse()
            data = json.loads(res.read())
            if data["status"] == "SUCCESS":
                break
            else:
                retries+=1
        except:
            retries+=1
    for account in cost_config:
        foundit = False
        for datum in data["data"]["data"]:
            if datum["id"] == account["number"]:
                thisdata = {
                    "account" : account["name"],
                    "total" : datum["cost"],
                    "trend" : datum["costTrend"]
                    }
                outdata.append(thisdata)
                foundit = True
        if not foundit:
            thisdata = {
                "account" : account["name"],
                "total" : 0,
                "trend" : 0
                }
            outdata.append(thisdata)
    return outdata

def main():
    token = os.environ['HARNESS_API_TOKEN']
    config = load_configuration("./config/config.json")
    data = load_perspective_costs(token, config['harness_application_costs'][0], 3, 2024, 28)
    for datum in data:
        print (datum["application"]+"\t"+str(datum["total"])+"\t"+str(datum["trend"])+"\t"+str(datum["forecast_pct_of_budget"]))
    #load_perspectives_budget_variances(token, config["harness_application_costs"][0])

if __name__ == "__main__":
    main()