import http.client
import json

from time import strftime, sleep
from utils.dateutils import days_in_month

def timespan_string(year_number,month_number):
    month = str(month_number).zfill(2)
    year = str(year_number).zfill(4)
    start_date = year+'-'+month+'-'+'01'
    if month == '12':
        end_date = str(year_number+1).zfill(4)+'-01-01'
    else:
        next_month = str(month_number+1).zfill(2)
        end_date = year+'-'+next_month+'-'+'01'
    return (start_date+'%2F'+end_date)

def first_day(month,year):
    out = str(year).zfill(4)+'-'+str(month).zfill(2)+'-01'
    return out

def last_day(month,year):
    out = str(year).zfill(4)+'-'+str(month).zfill(2)+'-'+str(days_in_month(month,year)).zfill(2)
    return out

def connect_with_retries(search_str,payload,headers,conn):
    retries = 0
    while (retries < 3):
        conn.request('POST', search_str, payload, headers)
        res = conn.getresponse()
        data = json.loads(res.read())
        if 'properties' in data:
            return data
        print('retrying')
        sleep(5)
        retries = retries + 1
    return None

def load_current_month_estimated_cost(token,subscription,name):
    conn = http.client.HTTPSConnection('management.azure.com')
    payload = '{\n  type: "Usage",\n  dataset: {\n    "granularity": "monthly",\n    "aggregation":{\n      "totalCost":{\n        "name":"Cost",\n        "function":"Sum"\n      }\n    }\n  },\n  timeframe: "MonthToDate"\n}'
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    search_str = '/subscriptions/'+subscription+'/providers/Microsoft.CostManagement/query?api-version=2021-10-01'
    data = connect_with_retries(search_str,payload,headers,conn)
    if data:
        actual = data['properties']['rows'][0][0]
    else:
        actual = 0
        return None
    #now get forecast
    search_str = '/subscriptions/'+subscription+'/providers/Microsoft.CostManagement/forecast?api-version=2021-10-01'
    data = connect_with_retries(search_str,payload,headers,conn)
    if data:
        forecast = data['properties']['rows'][0][0]
    else:
        forecast = 0
    current_month = int(strftime('%m'))
    current_year = int(strftime('%y'))+2000
    output = {
        'total': actual+forecast,
        'actual': actual,
        'forecast': forecast,
        'estimated': True,
        'name': name,
        'month': current_month,
        'year': current_year
    }
    return output

def load_past_month_cost(token,subscription,name,month,year):
    conn = http.client.HTTPSConnection('management.azure.com')
    payload = '{\n  type: "Usage",\n  dataset: {\n    "granularity": "monthly",\n    "aggregation":{\n      "totalCost":{\n        "name":"Cost",\n        "function":"Sum"\n      }\n    }\n  },\n  timeframe: "Custom",\n  timePeriod: {\n       from: "'+first_day(month,year)+'T00:00:00",\n       to:   "'+last_day(month,year)+'T23:59:59"\n   }\n}'
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    search_str = '/subscriptions/'+subscription+'/providers/Microsoft.CostManagement/query?api-version=2021-10-01'
    conn.request('POST', search_str, payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    actual = data['properties']['rows'][0][0]
    output = {
        'total': actual,
        'actual': actual,
        'forecast': 0,
        'estimated': False,
        'name': name,
        'month': month,
        'year': year
    }
    return output

def load_secure_score(token,subscription,name):
    conn = http.client.HTTPSConnection('management.azure.com')
    payload = ''
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    search_str = '/subscriptions/'+subscription+'/providers/Microsoft.Security/secureScores/ascScore?api-version=2020-01-01'
    conn.request('GET', search_str, payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    output = {
        'score': data['properties']['score']['percentage']*100,
        'subscription': name
    }
    return output

def load_compliance_score(token,subscription,standard):
    conn = http.client.HTTPSConnection('management.azure.com')
    payload = ''
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    search_str = '/subscriptions/'+subscription+'/providers/Microsoft.Security/regulatoryComplianceStandards/'+standard+'?api-version=2019-01-01-preview'
    conn.request('GET', search_str, payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    if 'error' in data:
        output = {
            'pass' : None,
            'fail' : None,
            'skip' : None
        }
    else:
        output = {
            'pass': data['properties']['passedControls'],
            'fail': data['properties']['failedControls'],
            'skip': data['properties']['skippedControls'],
        }
    return output

def load_availability(token, search_str, year_number, month_number): 
    conn = http.client.HTTPSConnection('management.azure.com')
    search_str = search_str.replace('#{timespan}#',timespan_string(year_number,month_number))
    payload = ''
    headers = {'Authorization': token }
    conn.request('GET', search_str, payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    try:
        total = data['Tables'][0]['Rows'][0][0]
        total = total if total != 'NaN' else None
    except:
        total = None
    return total

def load_aws_secure_score(token, subscription_id, name, aws_rg, aws_connector):
    conn = http.client.HTTPSConnection('management.azure.com')
    payload = ''
    headers = {'Authorization': token, 'Content-Type': 'application/json'}
    search_str = f'/subscriptions/{subscription_id}/resourceGroups/{aws_rg}/providers/Microsoft.Security/securityConnectors/{aws_connector}/providers/Microsoft.Security/secureScores?api-version=2020-01-01'
    conn.request('GET', search_str, payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    score = data['value'][0]['properties']['score']['percentage'] * 100
    score = round(score, 2)
    output = {
        'score': score,
        'subscription': name
    }
    return output
