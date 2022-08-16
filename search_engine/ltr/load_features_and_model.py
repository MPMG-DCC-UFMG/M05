import json
import requests
from urllib.parse import urljoin

def save_model(es_host, feature_set="m05"):
    """ Save the ranklib model in Elasticsearch """
    import requests
    import json
    from urllib.parse import urljoin
    modelPayload = {
        "model": {
            "name": "m05_model",
            "model": {
                "type": "model/linear"
            }
        }
    }

    # Force the model cache to rebuild
    path = "_ltr/_clearcache"
    fullPath = urljoin(es_host, path)
    print("POST %s" % fullPath)
    resp = requests.post(fullPath)
    if (resp.status_code >= 300):
        print(resp.text)

    modelContent =  "{\"feature_1\" : 0.3,\"feature_2\" : 0.5,\"feature_3\" : 0.1,\"feature_4\" : 0.1}"
    path = "_ltr/_featureset/%s/_createmodel" % feature_set
    fullPath = urljoin(es_host, path)
    modelPayload['model']['model']['definition'] = modelContent
    print("POST %s" % fullPath)
    resp = requests.post(fullPath, json.dumps(modelPayload), headers={"Content-Type": "application/json"})
    print(resp.status_code)
    if (resp.status_code >= 300):
        print(resp.text)

def get_feature(feature_name):
    with open('./features/feature_%s.json' % feature_name) as f:
        return json.loads(f.read())

def each_feature():
    features = [1, 2, 3, 4]
    try:
        for feature in features:
            parsedJson = get_feature(feature)
            template = parsedJson['query']
            feature_spec = {
                "name": "feature_%s" % feature,
                "params": ["consulta"],
                "template": template
            }
            print("Loading feature %s" % feature)
            print(feature_spec)
            yield feature_spec
    except IOError:
        pass

def load_features(es_host, feature_set_name='m05'):
    feature_set = {
        "featureset": {
            "name": feature_set_name,
            "features": [feature for feature in each_feature()]
        }
    }
    path = "_ltr/_featureset/%s" % feature_set_name
    full_path = urljoin(es_host, path)
    print("POST %s" % full_path)
    print(json.dumps(feature_set, indent=2))
    resp = requests.post(full_path, json.dumps(feature_set), headers={"Content-Type": "application/json"})
    print("%s" % resp.status_code)
    print("%s" % resp.text)

def init_store(es_host):
    path = urljoin(es_host, '_ltr')
    print("DELETE %s" % path)
    resp = requests.delete(path)
    print("%s" % resp.status_code)
    print("PUT %s" % path)
    resp = requests.put(path)
    print("%s" % resp.status_code)

if __name__ == "__main__":
    from time import sleep
    es_host='http://localhost:9200'
    init_store(es_host)
    sleep(1)
    load_features(es_host)
    save_model(es_host, feature_set="m05")