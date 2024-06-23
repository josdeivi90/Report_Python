def calc_cost_per(totaldollar,data,subscription):
    total_users = 0
    for app in data:
        if "FTHub Production" in subscription:
            total_users += app["production"]
        elif "QA" in subscription:
            total_users += app["QA"]
        elif "Sandbox" in subscription:
            total_users += app["sandbox"]
        elif "PreProduction" in subscription:
            total_users += app["preprod"]
        elif "Demo" in subscription:
            total_users += app["demo"]
        else:
            return None
    if total_users == 0:
        return 0
    else:
        return totaldollar/total_users