import json

def load_configuration(filename):
    with open(filename) as f:
        data = json.load(f)
    return data