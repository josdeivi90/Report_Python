import os  # Importa el módulo para interactuar con el sistema operativo.
from authentication.aztokenizer import getAzureToken  # Importa la función getAzureToken desde el módulo authentication.aztokenizer.

# Obtiene el ID del inquilino de Azure desde las variables de entorno.
TENANT_ID = os.environ['AZURE_TENANT_ID']

# Inicializa un diccionario vacío para almacenar los tokens.
TOKENS = {}

# Define una función para obtener un token de Azure para una suscripción dada.
def getting_azure_token(subscription):
    # Obtiene el nombre de la suscripción desde el diccionario de suscripción.
    subscription_name = subscription['name']
    
    try:
        # Obtiene el token de Azure llamando a la función getAzureToken con los parámetros adecuados.
        token = 'Bearer ' + getAzureToken(os.environ[subscription['token_name']], TENANT_ID)
        # Almacena el token en el diccionario TOKENS con el nombre de la suscripción como clave.
        TOKENS[subscription_name] = token
    except:
        # Si ocurre una excepción, imprime un mensaje indicando que no se encontró el token para la suscripción.
        print(f'Token not found for subscription: {subscription_name}')
        token = None

    # Si el token es None y el nombre de la suscripción es 'az2p-0118-LeMans_Production-AS-C71', lanza una excepción.
    if token == None and subscription_name == 'az2p-0118-LeMans_Production-AS-C71':
        raise Exception('Token not found for subscription: ' + subscription_name)

    # Retorna el token.
    return token

    
   
def which_token(subscription):
    subscription_name = subscription['name']
    
    if subscription_name in TOKENS:
        return TOKENS[subscription_name]
    
    print(f'...Getting Azure Token for {subscription_name}...')
    token = getting_azure_token(subscription)
    return token
    