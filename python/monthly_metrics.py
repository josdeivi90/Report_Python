import getopt, sys, os, re, json
from datetime import datetime, timezone
from loaders.azloader import load_availability, load_current_month_estimated_cost, load_past_month_cost, load_secure_score, load_compliance_score
from loaders.pdloader import load_oncall_metrics
from utils.console_out import dump_metrics_to_console
from utils.configuration import load_configuration
from utils.json_file_da import add_metrics_to_json_data, get_one_month_data
from loaders.gainsightloader import load_all_sessions, load_new_users, load_unique_users, load_user_sessions
from loaders.harnessloader import load_perspective_costs, load_aws_account_cost
from authentication.get_azure_tokens import which_token
from utils.json_file_da import load_json_data
from loaders.prismaloader import get_prisma_data
from loaders.synthetic_test_loader import synthetic_test_loader
from loaders.azloader import load_aws_secure_score

temporary_data = load_json_data('./data/json_data.json')[-1] #Temporary


def main():

    current_month = int(datetime.now(timezone.utc).strftime('%m'))
    current_year = int(datetime.now(timezone.utc).strftime('%y'))+2000
    current_day = int(datetime.now(timezone.utc).strftime('%d'))

    argv = sys.argv[1:]
    METRIC_MONTH = current_month
    METRIC_YEAR = current_year
    COST_ONLY = False

    try:
        opts, args = getopt.getopt(argv,'m:y:c', ['month=','year=','costonly'])
    except getopt.GetoptError:
        print ('monthly_metrics.py -m <month> -y <year>')
        sys.exit(2)
    
    for opt, arg in opts:
        if opt == '-h':
            print ('monthly_metrics.py -m <month> -y <year>')
            sys.exit()
        elif opt in ('-m', '--month'):
            METRIC_MONTH = int(arg)
        elif opt in ('-y', '--year'):
            METRIC_YEAR = int(arg)
        elif opt in ('-c', '--costonly'):
            COST_ONLY = True

    config = load_configuration('./config/config.json')

    #if we're only doing partial, we need to load the existing data
    if COST_ONLY:
        json_data = get_one_month_data(METRIC_YEAR,METRIC_MONTH)
        availability_data = json_data['availability_data']
        pd_data = json_data['pd_data']
        cost_data = json_data['cost_data']
        app_cost_data = json_data['app_cost_data']
        security_data = json_data['security_data']
        usage_data = json_data['usage_data'] 

    #Gather availability metrics
    if not COST_ONLY:
        print ('...Acquiring Azure availability...')
        subscriptions = config['az_subscription_costs']
        az_availability_metrics = config['az_availability_metrics']
        availability_data = [] 
        
        for subscription in subscriptions:
            search_str = '/subscriptions/#{subscription_id}#/resourceGroups/#{resourcegroup_name}#/providers/#{provider}#/workspaces/#{workspace_name}#/api/query?api-version=2017-01-01-preview&query=#{general_query}##{filter}##{operation}#&timespan=#{timespan}#'
            
            token = which_token(subscription)
            search_str = search_str.replace('#{subscription_id}#', subscription['id'])
            search_str = search_str.replace('#{workspace_name}#', subscription['workspace_name'])
            search_str = search_str.replace('#{resourcegroup_name}#', subscription['resourcegroup_name'])
            for az_availability_metric in az_availability_metrics:
                search_str = search_str.replace('#{provider}#', az_availability_metric['provider'])
                search_str = search_str.replace('#{general_query}#', az_availability_metric['general_query'])
                search_str = search_str.replace('#{operation}#', az_availability_metric['operation'])
                
                for service in az_availability_metric['services']:
                    search_str = search_str.replace('#{filter}#', service['filter'])
                    service_data = {    
                        'availability' : load_availability(token, search_str, METRIC_YEAR, METRIC_MONTH),
                        'year' : METRIC_YEAR,
                        'month' : METRIC_MONTH,
                        'service' : service['name'],
                        'subscription' : subscription['short_name']
                    }
                    availability_data.append(service_data)
                    search_str = search_str.replace(service['filter'],'#{filter}#')
                search_str = search_str.replace(az_availability_metric['provider'],'#{provider}#')
                search_str = search_str.replace(az_availability_metric['general_query'],'#{general_query}#')
                search_str = search_str.replace(az_availability_metric['operation'],'#{operation}#')

    #Gather PagerDuty metrics
    if not COST_ONLY:
        print ('...Pulling PagerDuty performance...')
        teams = config['pd_team_metrics']
        pd_data = []
        for team in teams:
            data = load_oncall_metrics(team,METRIC_YEAR,METRIC_MONTH,False)
            team_data = {
                'team' : team,
                'data' : data
            }
            pd_data.append(team_data)
    
    #Gather cost metrics
    if not COST_ONLY:
        print ('...Calculating cluster costs...')
        subscriptions = config['az_subscription_costs']
        cost_data = []
        for subscription in subscriptions:
            token = which_token(subscription)
            
            if token: #Just in case we don't have a token for this subscription or it's broken
                if METRIC_MONTH == current_month:
                    data = load_current_month_estimated_cost(token,subscription['id'],subscription['name'])
                else:
                    data = load_past_month_cost(token,subscription['id'],subscription['name'],METRIC_MONTH,METRIC_YEAR)
                if data:
                    cost_data.append(data)
                    continue
            
            print(f'WARNING: Invalid token for {subscription["name"]}')

            if temporary_data['month'] == METRIC_MONTH: 
                for costs in temporary_data['cost_data']:
                    if costs['name'] == subscription['name']:
                        cost_data.append(costs)

    #gather security score metrics
    if not COST_ONLY:
        print ('...Securing secure scores...')
        subscriptions = config['az_subscription_costs']
        security_data = []
        for subscription in subscriptions:
            token = which_token(subscription)

            if token: #Temporary
                try:
                    data = load_secure_score(token,subscription['id'],subscription['name'])
                    data['iso_27001_2013'] = load_compliance_score(token,subscription['id'],'ISO%2027001%3A2013')
                    data['azure_cis_1_4_0'] = load_compliance_score(token,subscription['id'],'CIS-Azure-Foundations-v1.4.0')
                    data['soc_2_type_2'] = load_compliance_score(token, subscription['id'], 'SOC%202')
                    print(f'Sub: {subscription["id"]}')
                    print(data['soc_2_type_2'])
                    security_data.append(data)
                    continue
                except:
                    print(f'WARNING: Invalid token for {subscription["name"]}')
            
            if temporary_data['month'] == METRIC_MONTH:
                for old_security_data in temporary_data['security_data']:
                    if old_security_data['subscription'] == subscription['name']:
                        security_data.append(old_security_data)
 
        print ('...Securing AWS secure scores...')
        aws_secure_score_data = []
        for subscription in subscriptions:
            if not 'aws_account_name' in subscription:
                continue
            token = which_token(subscription)
            aws_score_data = load_aws_secure_score(token,
                                         subscription['id'],
                                         subscription['aws_account_name'],
                                         subscription['aws_integration_rg'],
                                         subscription['aws_security_connector']
                                         )
            aws_secure_score_data.append(aws_score_data)

    #gather gainsight metrics
    if not COST_ONLY:
        print ('...Gathering Gainsight gauges...')
        user_sessions = load_user_sessions(METRIC_YEAR,METRIC_MONTH,config['gs_property_keys'])
        all_sessions = load_all_sessions(METRIC_YEAR,METRIC_MONTH,config['gs_property_keys'])
        new_users = load_new_users(METRIC_YEAR,METRIC_MONTH,config['gs_property_keys'])
        active_users = load_unique_users(METRIC_YEAR,METRIC_MONTH,config['gs_property_keys'])
        usage_data = {
            'user_sessions' : user_sessions,
            'all_sessions' : all_sessions,
            'new_users' : new_users,
            'active_users' : active_users
        }

    #harness harness metrics
    harness_token = os.environ['HARNESS_API_TOKEN']
    if not COST_ONLY:
        print ('...Harnessing Harness harnesses...')
        if METRIC_MONTH != current_month:
            current_day = 0
        app_cost_data = load_perspective_costs(harness_token, config['harness_application_costs'][0], METRIC_MONTH, METRIC_YEAR, current_day)
    
    print ('...kicking Harness to get AWS costs...')
    if METRIC_MONTH != current_month:   
        current_day = 0
    aws_cost_data = load_aws_account_cost(harness_token, config['aws_account_costs'],'2FM_9exYT0SBwBAAikfuDg',
        config['harness_application_costs'][0]['account_id'],METRIC_MONTH, METRIC_YEAR, current_day)
    
    #prisma cloud metrics
    if not COST_ONLY:
        print ('...Prisma Clouding...')
        prisma_data = get_prisma_data()

    #Gather synthetic test results
    if not COST_ONLY:
        synthetic_tests_data = synthetic_test_loader(config, METRIC_YEAR, METRIC_MONTH)
        
    dump_metrics_to_console(availability_data, pd_data, cost_data, aws_cost_data, app_cost_data, security_data, usage_data)

    #write to json
    print('...Updating JSON data...')
    utc_now_dt = datetime.now(timezone.utc).strftime('%m/%d/%Y, %H:%M:%S')
    data = {
        'year' : METRIC_YEAR,
        'month' : METRIC_MONTH,
        'availability_data' : availability_data,
        'pd_data' : pd_data,
        'cost_data' : cost_data,
        'aws_cost_data' : aws_cost_data,
        'app_cost_data' : app_cost_data,
        'security_data' : security_data,
        'usage_data' : usage_data,
        'prisma_data' : prisma_data,
        'synthetic_tests_data' : synthetic_tests_data,
        'aws_secure_score_data' : aws_secure_score_data,
        'utc_now_dt' : utc_now_dt
    }

    add_metrics_to_json_data(data)

if __name__ == '__main__':
    main()