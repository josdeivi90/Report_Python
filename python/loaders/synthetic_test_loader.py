from authentication.get_azure_tokens import which_token
from loaders.azloader import load_availability

def synthetic_test_loader(config, METRIC_YEAR, METRIC_MONTH):
    print ('...Acquiring Synthetic Test results...')
    
    subscriptions = config['az_subscription_costs']
    synthetic_test_metrics = config['synthetic_test_metrics']
    synthetic_tests_data = [] 
    search_str = '/subscriptions/#{subscription_id}#/resourceGroups/#{resourcegroup_name}#/providers/#{provider}#/workspaces/#{workspace_name}#/api/query?api-version=2017-01-01-preview&query=#{query}#&timespan=#{timespan}#'
    
    for subscription in subscriptions:
        if subscription['name'] != 'FTHub Production':
            continue
        
        token = which_token(subscription)
        search_str = search_str.replace('#{subscription_id}#', subscription['id'])
        search_str = search_str.replace('#{workspace_name}#', subscription['workspace_name'])
        search_str = search_str.replace('#{resourcegroup_name}#', subscription['resourcegroup_name'])
        
        for sub in synthetic_test_metrics:
            search_str = search_str.replace('#{provider}#', sub['provider'])
            search_str = search_str.replace('#{query}#', sub['general_query'])
            for service in sub['services']:
                service_name = service['name']
                no_spaces_service = service_name.replace(' ', '+')

                if 'filter' in service:
                    no_spaces_service += service['filter']

                search_str = search_str.replace('#{service}#', no_spaces_service)
                
                test_data = {
                    'result' : load_availability(token, search_str, METRIC_YEAR, METRIC_MONTH),
                    'test_name' : service_name
                }

                synthetic_tests_data.append(test_data)
                search_str = search_str.replace(no_spaces_service,'#{service}#')

    return synthetic_tests_data