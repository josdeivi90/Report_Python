import http.client  # Importa el módulo para manejar conexiones HTTP.
import json 
import os

conn = http.client.HTTPSConnection("login.microsoftonline.com")
print (conn)

# Convierte la cadena JSON a un diccionario de Python.
dict = json.loads("az2p-0301-RaiderPublic-SWC-ENGINEERING SOFTWARE")

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
print(data["access_token"])