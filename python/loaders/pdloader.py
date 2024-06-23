import http.client
import json
import os
import time
from utils.dateutils import days_in_month

# pdloader -> PagerDuty API loader stuff

def load_teams():
    conn = http.client.HTTPSConnection("api.pagerduty.com")
    payload = ''
    pd_token = os.environ['PAGERDUTY_API_KEY']
    headers = {
        'Authorization': 'Token token='+pd_token,
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Content-Type': 'application/json'
    }
    conn.request("GET", "/teams?limit=20&offset=0&total=false",
                 payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    teams = data["teams"]
    return teams


def load_oncall_metrics(team, year, month, major):
    majorstr = "false"
    if major:
        majorstr = "true"
    pd_token = os.environ['PAGERDUTY_API_KEY']
    conn = http.client.HTTPSConnection("api.pagerduty.com")
    startdate = str(year)+"-"+str(month).zfill(2)+"-01T00:00:00"
    enddate = str(year)+"-"+str(month).zfill(2)+"-" + \
        str(days_in_month(month,year)).zfill(2)+"T23:59:59"
    payloadMTTA = json.dumps({
        "filters": {
            "created_at_start": startdate,
            "created_at_end": enddate,
            "urgency": "high",
            "team_ids": [
                ""+team["id"]+""
            ]
        },
        "aggregate_unit": "month",
        "time_zone": "Etc/UTC"
    })
    payloadMTTRBF = json.dumps({
        "filters": {
            "created_at_start": startdate,
            "created_at_end": enddate,
            "urgency": "high",
            "team_ids": [
                ""+team["id"]+""
            ],
            "priority_ids": [
                "PD6PLMV",
                "PZX1LN5",
                "PVKDKXF",
                "PSOSJIS",
                None
            ]
        },
        "aggregate_unit": "month",
        "time_zone": "Etc/UTC"
    })
    
    headers = {
        'Authorization': 'Token token='+pd_token,
        'X-EARLY-ACCESS': 'analytics-v2',
        'Accept': 'application/vnd.pagerduty+json;version=2',
        'Content-Type': 'application/json',
        'Content-Type': 'application/json'
    }
    
    #Load MTTA
    conn.request("POST", "/analytics/metrics/incidents/all", payloadMTTA, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    if (len(data["data"]) > 0):
        stats = data["data"][0]
        if stats["mean_seconds_to_first_ack"] is None:
            mtta = None
        else:
            mtta = int(stats["mean_seconds_to_first_ack"]/60)
    else:
        mtta = None 

    time.sleep(2)

    #Load MTTR and MTBF
    conn.request("POST", "/analytics/metrics/incidents/all", payloadMTTRBF, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    if (len(data["data"]) > 0):
        stats = data["data"][0]
        if stats["mean_seconds_to_resolve"] is None:
            mttr = None
        else:
            mttr = int(stats["mean_seconds_to_resolve"]/60)
        if stats["total_incident_count"] is None:
            mtbf = None
        else:
            mtbf = round(24*days_in_month(month,year)/stats["total_incident_count"])
    else:
        mttr = None
        mtbf = None

    output = {
        "MTTA": mtta,
        "MTTR": mttr,
        "MTBF": mtbf
    }
    return output
