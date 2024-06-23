import http.client
import json

def getAzureToken(spn_json, tenant_id):
    conn = http.client.HTTPSConnection("login.microsoftonline.com")
    dict = json.loads(spn_json)

    payload = "grant_type=client_credentials&resource=https%3A%2F%2Fmanagement.azure.com%2F&client_id="+dict["clientId"]+"&client_secret="+dict["clientSecret"]
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    conn.request("POST", "/"+tenant_id+"/oauth2/token", payload, headers)
    res = conn.getresponse()
    data = json.loads(res.read())
    return data["access_token"]
