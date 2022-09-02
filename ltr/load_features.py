import json
import requests
from urllib.parse import urljoin
from os import listdir
from os.path import isfile, join

def save_model(es_host, feature_set="m05"):
    """ Save the rank model in Elasticsearch """
    modelPayload = {
        "model": {
            "name": "m05_model",
            "model": {
                "type": "model/xgboost+json"
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
    with open('./ltr/xgboost_model.json') as modelFile:
        modelContent = modelFile.read()
        path = "_ltr/_featureset/%s/_createmodel" % feature_set
        fullPath = urljoin(es_host, path)
        modelPayload['model']['model']['definition'] = modelContent
        print("POST %s" % fullPath)
        resp = requests.post(fullPath, json.dumps(modelPayload), headers={"Content-Type": "application/json"})
        print(resp.status_code)
        if (resp.status_code >= 300):
            print(resp.text)

def get_feature(feature_name):
    with open('./ltr/features/%s.json' % feature_name) as f:
        return json.loads(f.read())

def each_feature():
    features = [f[:-5] for f in listdir("./ltr/features") if isfile(join("./ltr/features", f))]
    with open('./ltr/featmap.txt', "w") as f:
        try:
            for idx, feature in enumerate(features):
                parsedJson = get_feature(feature)
                template = parsedJson['query']
                feature_spec = {
                    "name": "%s" % feature,
                    "params": ["consulta"],
                    "template": template
                }
                print("Loading feature %s" % feature)
                # feature types: use i for indicator and q for quantity
                f.write(f"{idx} {feature} q" + "\n")
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