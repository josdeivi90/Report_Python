from utils.getting_pd_from_jsondata import get_pd_from_json_data
from utils.calculate_performance_score import get_performance_points

def replace_traffic_light(htmlstr, whichlight, score):
    if score=='green':
        htmlstr = htmlstr.replace('$'+whichlight+'_green$','#00FF00')
    else:
        htmlstr = htmlstr.replace('$'+whichlight+'_green$','#006000')
    if score=='yellow':
        htmlstr = htmlstr.replace('$'+whichlight+'_yellow$','#FFFF00')
    else:
        htmlstr = htmlstr.replace('$'+whichlight+'_yellow$','#606000')
    if score=='red':
        htmlstr = htmlstr.replace('$'+whichlight+'_red$','#FF0000')
    else:
        htmlstr = htmlstr.replace('$'+whichlight+'_red$','#600000')
    return htmlstr

def set_traffic_light_color(green_lower_threshold, yellow_lower_threshold, score):
    if score >= green_lower_threshold:
        return 'green'
    elif score <= green_lower_threshold and score >= yellow_lower_threshold:
        return 'yellow'
    else:
        return 'red'

def set_cost_light_color(green_upper_threshold, yellow_upper_threshold, score):
    if score < green_upper_threshold:
        return 'green'
    elif score > yellow_upper_threshold:
        return 'red'
    else:
        return 'yellow'

def set_security_light(data):
    green_lower_threshold = 80
    yellow_lower_threshold = 60
    last_month_data = data[-1]
    security_data = last_month_data['security_data']
    for sub in security_data:
        if sub['subscription'] == 'FTHub Production':
            security_score = sub['score']
    traffic_light_color = set_traffic_light_color(green_lower_threshold, yellow_lower_threshold, security_score)
    return traffic_light_color
    
def set_availability_light(data):
    green_lower_threshold = 99.99
    yellow_lower_threshold = 99
    last_month_availability = data[-1]['availability_data']
    availability = {}
    for sub in last_month_availability:
        if sub['subscription'] == 'prod':
            availability[sub['service']] = sub['availability']
    min_availability_value = min(availability.values())

    traffic_light_color = set_traffic_light_color(green_lower_threshold, yellow_lower_threshold, min_availability_value)
    if traffic_light_color != 'green':
        for service in availability:
            availability[service] = {
                'availability' : availability[service],
                'color': set_traffic_light_color(green_lower_threshold, yellow_lower_threshold, availability[service])
            }
        return availability, traffic_light_color
    return None, traffic_light_color

def set_performance_light(data): 
    green = 5
    red = 12
    team_score = {
        'green' : 0,
        'yellow' : 2,
        'red' : 5,
    }
    pd_data = get_pd_from_json_data(data)
    points = []

    performance = {}
    
    for team in pd_data:
        team_data = pd_data[team]
        
        mtta_points = get_performance_points(team_data, 'MTTA', team_score)
        points.append(mtta_points)

        mttr_points = get_performance_points(team_data, 'MTTR', team_score)
        points.append(mttr_points)

        performance[team] = {
            'MTTA' : mtta_points,
            'MTTR' : mttr_points
        }

    score = sum(points)
    if score < green:
        metric_color = 'green'
    elif score > red:
        metric_color = 'red'
    else:
        metric_color = 'yellow'
    
    if metric_color != 'green':
        for team in performance:
           for metric in performance[team]:
               color = [k for k, v in team_score.items() if v == performance[team][metric]][0]
               performance[team][metric] = { 
                     'score' : performance[team][metric],
                     'color' : color
               }
        return performance, metric_color
    
    return None, metric_color

def set_cost_light(data):
    green_upper_threshold = 110
    yellow_upper_threashold = 150
    last_month_data = data[-1]
    app_cost_data = last_month_data['app_cost_data']
    total_cost = 0
    for app in app_cost_data:
        total_cost = +app['total']
    weighted_pct = 0
    for app in app_cost_data:
        if 'forecast_pct_of_budget' in app:
            weighted_pct +=((app['total']/total_cost)*(app['forecast_pct_of_budget']/100))
    traffic_light_color = set_cost_light_color(green_upper_threshold, yellow_upper_threashold, weighted_pct)
    
    if traffic_light_color != 'green':
        cost_data = {}
        for app in app_cost_data:
            cost_data[app["application"]] = {
                'total' : app["total"],
                'color': set_cost_light_color(green_upper_threshold, yellow_upper_threashold, app["forecast_pct_of_budget"])
            }
        print ("cost data: ", cost_data)
        return cost_data, traffic_light_color

    return None, traffic_light_color
