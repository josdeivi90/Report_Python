
def output_pd_data(team, data):
    print("*** "+team["name"]+" ***")
    if data["MTTA"] is not None:
        print("MTTA = %d minutes" % data["MTTA"])
    else:
        print("MTTA = N/A")
    if data["MTTR"] is not None:
        print("MTTR = %d minutes " % data["MTTR"])
    else:
        print("MTTR = N/A")
    if data["MTBF"] is not None:
        print("MTBF = %d hours" % data["MTBF"])
    else:
        print("MTBF = N/A")

def output_availability_data(data):
    try:
        print("Availability for "+data["service"]+" - "+
            str(data["month"]).zfill(2)+"/"+str(data["year"])+
            " - {:.5f}".format(data["availability"])+"%")
    except:
        print("Availability for "+data["service"]+" - "+
            str(data["month"]).zfill(2)+"/"+str(data["year"])+
            str(data["availability"])+"%")

def output_cost_data(data):
    totaldollars =  "${:.2f}".format(data["total"])
    est = ""
    if data["estimated"]:
        est = "Estimated "
    print(est+"Azure cost for subscription "+data["name"]+" "+str(data["month"]).zfill(2)+"/"+str(data["year"]).zfill(4)+" "+totaldollars)

def output_aws_cost_data(data):
    print("AWS cost for account "+data["account"]+" is " "${:.2f}".format(data["total"])+" with trend "+"${:.2f}".format(data["trend"]))

def output_perspective(data):
    print("Cost for perspective "+data["application"]+" = $"+str(data["total"])+" trend = %"+str(data["trend"]))


def output_secure_score_data(data):
    print("Current Secure Score for "+data["subscription"]+" - {:.2f}".format(data["score"])+"%")
    #print("     SOC TSP - "+str(data["soc_tsp"]["pass"])+"/"+str(data["soc_tsp"]["fail"])+"/"+str(data["soc_tsp"]["skip"]))
    print("     ISO 27001:2013 - "+str(data["iso_27001_2013"]["pass"])+"/"+str(data["iso_27001_2013"]["fail"])+"/"+str(data["iso_27001_2013"]["skip"]))
    print("     Azure CIS 1.4.0 - "+str(data["azure_cis_1_4_0"]["pass"])+"/"+str(data["azure_cis_1_4_0"]["fail"])+"/"+str(data["azure_cis_1_4_0"]["skip"]))


def output_usage_data(data):
    print("Gainsight metric: service,production,QA,sandbox,preprod,demo")
    for service in data["user_sessions"]:
        print ("user_sessions: "+service["name"]+","+str(service["production"])+","+str(service["QA"])+","+str(service["sandbox"])+","+str(service["preprod"])+","+str(service["demo"]))
    for service in data["all_sessions"]:
        print ("all_sessions: "+service["name"]+","+str(service["production"])+","+str(service["QA"])+","+str(service["sandbox"])+","+str(service["preprod"])+","+str(service["demo"]))
    for service in data["new_users"]:
        print ("new_users: "+service["name"]+","+str(service["production"])+","+str(service["QA"])+","+str(service["sandbox"])+","+str(service["preprod"])+","+str(service["demo"]))
    for service in data["active_users"]:
        print ("active_users: "+service["name"]+","+str(service["production"])+","+str(service["QA"])+","+str(service["sandbox"])+","+str(service["preprod"])+","+str(service["demo"]))

def dump_metrics_to_console(availability_data, pd_data, cost_data, aws_cost_data, app_cost_data, security_data, usage_data):
    for cluster in availability_data:
        output_availability_data(cluster)
    for team in pd_data:
        output_pd_data(team["team"], team["data"])
    for cost in cost_data:
        output_cost_data(cost)
    for cost in aws_cost_data:
        output_aws_cost_data(cost)
    for perspective in app_cost_data:
        output_perspective(perspective)
    for score in security_data:
        output_secure_score_data(score)
    output_usage_data(usage_data)

