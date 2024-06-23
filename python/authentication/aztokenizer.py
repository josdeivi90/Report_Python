import http.client  # Importa el módulo para manejar conexiones HTTP.
import json        # Importa el módulo para manejar datos en formato JSON.

# Define una función para obtener un token de acceso de Azure.
def getAzureToken(spn_json, tenant_id):
    # Establece una conexión HTTPS con el servidor de autenticación de Microsoft.
    conn = http.client.HTTPSConnection("login.microsoftonline.com")
    
    # Convierte la cadena JSON a un diccionario de Python.
    dict = json.loads(spn_json)

    # Construye el payload (datos de la solicitud) para la autenticación.
    payload = (
        "grant_type=client_credentials"
        "&resource=https%3A%2F%2Fmanagement.azure.com%2F"
        "&client_id=" + dict["clientId"] +
        "&client_secret=" + dict["clientSecret"]
    )
    
    # Define los encabezados de la solicitud HTTP.
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    # Envía una solicitud POST al servidor de autenticación con el payload y los encabezados.
    conn.request("POST", "/" + tenant_id + "/oauth2/token", payload, headers)
    
    # Obtiene la respuesta del servidor.
    res = conn.getresponse()
    
    # Lee el cuerpo de la respuesta y lo convierte de JSON a un diccionario de Python.
    data = json.loads(res.read())
    
    # Retorna el token de acceso obtenido de la respuesta.
    return data["access_token"]

