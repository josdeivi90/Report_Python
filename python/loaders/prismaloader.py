import http.client, json, re
from authentication.get_prisma_token import prisma_get_token

exempted_namespaces = '(.*runner|harness.*)|monitor|splunk|ftegaas|kube-system|kured|default|kafka|rabbitmq|cert-manager|keda|flux-system|gatekeeper-system|twistlock|selenium-grid|reloader'

dev_registries = '.*(plexdev.azurecr.io).*'

namespaces_sorted_by_app = {
        'FT Vault' : [],
        'FT Remote Access' : ['sra'],
        'FT Common' : ['common-services'],
        'FT Edge Manager' : ['eaas'],
        'FT Optix' : ['asem'],
        'FT DataMosaix' : ['datamosaix', 'observability'],
        'FT TwinStudio' : [],
        'Testing' : []
    }

def prisma_loader():
    token = prisma_get_token()
    conn = http.client.HTTPSConnection('us-east1.cloud.twistlock.com')
    payload = ''
    headers = {
      'Accept': 'application/json; charset=UTF-8',
      'Content-Type': 'application/json',
      'Authorization': f'Bearer {token}'
    }
    data = []
    isData = True
    counter = 0

    while isData:
        try:
            conn.request('GET', f'/us-2-158255950/api/v1/images?offset={counter}&limit=100&clusters=aks-eastus2-production*', payload, headers)
            res = conn.getresponse()
            response = res.read()
            response = json.loads(response)
            data+=response
            counter += 100
            if 'too many requests' in str(response):
                print('Too many requests!!!!!')
                break
        except:
            #print('No more data!!')
            isData = False
    return data

def sort_images_by_namespace(data):
    images = {}
    for image in data:
        namespaces = image['namespaces']
        namespaces = list(filter(lambda namespace: not re.match(exempted_namespaces, namespace, re.IGNORECASE), namespaces))
        
        if not len(namespaces):
            continue
        
        image_digest = image['repoDigests'][0]
        image_tags = image['repoTag']
        vulnerabilityDistribution = image['vulnerabilityDistribution']
        critical = vulnerabilityDistribution['critical']
        high = vulnerabilityDistribution['high']
        medium = vulnerabilityDistribution['medium']
        
        for namespace in namespaces:
            if namespace not in images:
                images[namespace] = {
                    'images' : {},
                    'total' : {
                        'critical' : 0,
                        'high' : 0,
                        'medium' : 0 
                    }
                }
            
            images[namespace]['images'][image_digest] = {
                'image' : image_tags,
                'vulnerabilityDistribution' : {
                    'critical' : critical,
                    'high' : high,
                    'medium' : medium
                }
            }

            images[namespace]['total']['critical'] += critical
            images[namespace]['total']['high'] += high
            images[namespace]['total']['medium'] += medium

    return images

def sort_images_by_app(images):
    images_vulnerabilities_by_app = []

    for namespace in images:
        if namespace == 'development':
            for image in images[namespace]['images']:
                application = ''
                if re.match('.*lemans-help-desk.*', image, re.IGNORECASE):
                    continue
                elif re.match('.*ui-framework.*', image, re.IGNORECASE):
                    application = 'FT Common'
                elif re.match('.*(l5x-stitcher|lcore|sprotty-typefox-server).*', image, re.IGNORECASE):
                    application = 'FT Vault'
                elif re.match('.*twinstudio.*', image, re.IGNORECASE):
                    application = 'FT TwinStudio'
                
                if application:
                    med_vulnerabilities = images[namespace]['images'][image]['vulnerabilityDistribution']['medium']
                    high_vulnerabilities = images[namespace]['images'][image]['vulnerabilityDistribution']['high']
                    critical_vulnerabilities = images[namespace]['images'][image]['vulnerabilityDistribution']['critical']
                    images_vulnerabilities_by_app = add_new_entry_to_images_vulnerabilities_by_app(med_vulnerabilities, high_vulnerabilities, critical_vulnerabilities, application, images_vulnerabilities_by_app)
            continue

        for app in namespaces_sorted_by_app:
            med_vulnerabilities = images[namespace]['total']['medium']
            high_vulnerabilities = images[namespace]['total']['high']
            critical_vulnerabilities = images[namespace]['total']['critical']
            
            is_testing_ns = True if re.match('.*testing-automation.*', namespace, re.IGNORECASE) and app == 'Testing' else False

            if namespace in namespaces_sorted_by_app[app] or is_testing_ns:
                images_vulnerabilities_by_app = add_new_entry_to_images_vulnerabilities_by_app(med_vulnerabilities, high_vulnerabilities, critical_vulnerabilities, app, images_vulnerabilities_by_app)

    return images_vulnerabilities_by_app


def get_prisma_data():
    data = prisma_loader()
    images_by_namespace = sort_images_by_namespace(data)
    images = sort_images_by_app(images_by_namespace)

    return images

def add_new_entry_to_images_vulnerabilities_by_app(medium, high, critical, app, images_vulnerabilities_by_app):
    current_apps = [ sub['application'] for sub in images_vulnerabilities_by_app ]

    if app not in current_apps:
        new_app = {
            'application' : app,
            'total' : {
                'critical' : critical,
                'high' : high,
                'medium' : medium
            }
        }
        images_vulnerabilities_by_app.append(new_app)
        return images_vulnerabilities_by_app
                
    for sub in images_vulnerabilities_by_app:
        if sub['application'] == app:
            sub['total']['critical'] += critical
            sub['total']['high'] += high
            sub['total']['medium'] += medium
            break

    return images_vulnerabilities_by_app