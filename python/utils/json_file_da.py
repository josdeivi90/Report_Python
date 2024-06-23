import json

def add_metrics_to_json_data(metrics):
    year = metrics['year']
    month = metrics['month']
    availability_data = metrics['availability_data']
    pd_data = metrics['pd_data']
    cost_data = metrics['cost_data']
    aws_cost_data = metrics['aws_cost_data']
    app_cost_data = metrics['app_cost_data']
    security_data = metrics['security_data']
    usage_data = metrics['usage_data']
    dt = metrics['utc_now_dt']
    prisma_data = metrics['prisma_data']
    synthetic_tests_data = metrics['synthetic_tests_data']
    aws_secure_score_data = metrics['aws_secure_score_data']



    data = load_json_data('./data/json_data.json')
    foundit = False
    for block in data:
        #find if month exists
        if (block['month'] == month) and (block['year'] == year):
            foundit = True
            #rewrite that block
            block['availability_data'] = availability_data
            block['pd_data'] = pd_data
            block['cost_data'] = cost_data
            block['aws_cost_data'] = aws_cost_data
            block['security_data'] = security_data
            block['usage_data'] = usage_data
            block['app_cost_data'] = app_cost_data
            block['prisma_data'] = prisma_data
            block['synthetic_tests_data'] = synthetic_tests_data
            block['aws_secure_score_data'] = aws_secure_score_data

    if not foundit: #adding new list member
        metric_dict = {
            'year' : year,
            'month' : month,
            'availability_data' : availability_data,
            'pd_data' : pd_data,
            'cost_data' : cost_data,
            'aws_cost_data' : aws_cost_data,
            'security_data' : security_data,
            'usage_data' : usage_data,
            'app_cost_data' : app_cost_data,
            'prisma_data' : prisma_data,
            'synthetic_tests_data' : synthetic_tests_data,
            'aws_secure_score_data' : aws_secure_score_data
            }
        
        data.append(metric_dict)
        
    #write out updated data
    data = add_zeros_to_data(data) #It adds zeros to months where data/subscription isn't found
    output_dict = {
        'datetime' : dt,
        'data' : data
    }

    write_to_json('./data/json_data.json',output_dict)

def write_to_json(filename,data):
    json_string = json.dumps(data, indent=4)
    with open(filename, 'w') as outfile:
        outfile.write(json_string)

def load_json_data(filename):
    with open(filename,'r+') as file:
        file_data = json.load(file)
    data = file_data['data']
    return data

def get_data_datetime(filename):
    with open(filename,'r+') as file:
        file_data = json.load(file)
    dt = file_data['datetime']
    return dt

def get_one_month_data(year,month):
    data = load_json_data('./data/json_data.json')
    for block in data:
        if (block['month'] == month) and (block['year'] == year):
            return block

def add_zeros_to_data(data):
    config_file = open('./config/config.json','r')
    config_data = json.load(config_file)
    config_file.close()
    new_data = add_zeros_to_cost_data(data, config_data)
    new_data = add_zeros_to_aws_data(new_data, config_data)
    return new_data

def add_zeros_to_cost_data(data, config_data):
    new_data = data
    for az_subscription in config_data['az_subscription_costs']:
        subscription_name = az_subscription['name']
        for data_block in new_data:
            subscription_exists = False
            month_costs = data_block['cost_data']
            for subscription_cost in month_costs:
                if subscription_cost['name'] == subscription_name: 
                    subscription_exists = True
                    break
            if not subscription_exists:
                empty_costs = {
                    'total': 0,
                    'actual': 0,
                    'forecast': 0,
                    'estimated': False,
                    'name': subscription_name,
                    'month': month_costs[0]['month'],
                    'year': month_costs[0]['year']
                }
                month_costs.append(empty_costs)
                empty_security_data = {
                        'score': 0,
                        'subscription': subscription_name,
                        # 'soc_tsp': {
                        #     'pass': None,
                        #     'fail': None,
                        #     'skip': None
                        # },
                        'iso_27001_2013': {
                            'pass': None,
                            'fail': None,
                            'skip': None
                        },
                        'azure_cis_1_4_0': {
                            'pass': None,
                            'fail': None,
                            'skip': None
                        }
                    }
                data_block['security_data'].append(empty_security_data)
    return new_data

def add_zeros_to_aws_data(data, config_data):
    new_data = data
    for aws_account in config_data['aws_account_costs']:
        aws_account_name = aws_account['name']
        for data_block in new_data:
            aws_account_exists = False
            month_costs = data_block['aws_cost_data']
            for aws_cost in month_costs:
                if aws_cost['account'] == aws_account_name: 
                    aws_account_exists = True
                    break
            if not aws_account_exists:
                empty_costs = {
                    'account': aws_account_name,
                    'total': 0,
                    'trend': 0
                }
                month_costs.append(empty_costs)
    return new_data
