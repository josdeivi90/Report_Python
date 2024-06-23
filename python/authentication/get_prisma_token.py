import http.client, os, json

def prisma_get_token():
    prisma_access = os.environ['PRISMACLOUD_ACCESS_KEY']
    prisma_secret = os.environ['PRISMACLOUD_SECRET_KEY']

    conn = http.client.HTTPSConnection('us-east1.cloud.twistlock.com')
    payload = json.dumps({
    'username': prisma_access,
    'password': prisma_secret
    })
    headers = { 'content-type' : 'application/json' }

    conn.request('POST', '/us-2-158255950/api/v1/authenticate', payload, headers)
    res = conn.getresponse()
    data = res.read()
    token = json.loads(data)['token']

    return token