import os
from authentication.aztokenizer import getAzureToken 

TENANT_ID = os.environ['AZURE_TENANT_ID']
TOKENS = {}

def getting_azure_token(subscription):
    subscription_name = subscription['name'] 
    try:
        token = 'Bearer '+getAzureToken(os.environ[subscription['token_name']], TENANT_ID)
        TOKENS[subscription_name] = token
    except:
        print(f'Token not found for subscription: {subscription_name}')
        token = None
    if token==None and subscription_name == 'az2p-0118-LeMans_Production-AS-C71':
        raise Exception('Token not found for subscription: '+subscription_name)
    return token
    
   
def which_token(subscription):
    subscription_name = subscription['name']
    
    if subscription_name in TOKENS:
        return TOKENS[subscription_name]
    
    print(f'...Getting Azure Token for {subscription_name}...')
    token = getting_azure_token(subscription)
    return token
    