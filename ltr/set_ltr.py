import os
from ltr.collect_features import log_features, build_train_file


def trainModel(trainingData, testData, modelOutput, whichModel=8):
    # java -jar RankLib-2.6.jar  -metric2t NDCG@4 -ranker 6 -kcv -train osc_judgments_wfeatures_train.txt -test osc_judgments_wfeatures_test.txt -save model.txt

    # For random forest
    # - bags of LambdaMART models
    #  - each is trained against a proportion of the training data (-srate)
    #  - each is trained using a subset of the features (-frate)
    #  - each can be either a MART or LambdaMART model (-rtype 6 lambda mart)
    cmd = "java -jar RankyMcRankFace-0.1.1.jar -metric2t NDCG@10 -bag 10 -srate 0.6 -frate 0.6 -rtype 6 -shrinkage 0.1 -tree 80 -ranker %s -train %s -test %s -save %s -feature features.txt" % (whichModel, trainingData, testData, modelOutput)
    print("*********************************************************************")
    print("*********************************************************************")
    print("Running %s" % cmd)
    os.system(cmd)
    pass


def partitionJudgments(judgments, testProportion=0.5):
    testJudgments = {}
    trainJudgments = {}
    from random import random
    for qid, judgment in judgments.items():
        draw = random()
        if draw <= testProportion:
            testJudgments[qid] = judgment
        else:
            trainJudgments[qid] = judgment

    return (trainJudgments, testJudgments)



def saveModel(esHost, scriptName, featureSet, modelFname):
    """ Save the ranklib model in Elasticsearch """
    import requests
    import json
    from urllib.parse import urljoin
    modelPayload = {
        "model": {
            "name": scriptName,
            "model": {
                "type": "model/ranklib",
                "definition": {
                }
            }
        }
    }

    # Force the model cache to rebuild
    path = "_ltr/_clearcache"
    fullPath = urljoin(esHost, path)
    print("POST %s" % fullPath)
    resp = requests.post(fullPath)
    if (resp.status_code >= 300):
        print(resp.text)

    with open(modelFname) as modelFile:
        modelContent = modelFile.read()
        path = "_ltr/_featureset/%s/_createmodel" % featureSet
        fullPath = urljoin(esHost, path)
        modelPayload['model']['model']['definition'] = modelContent
        print("POST %s" % fullPath)
        resp = requests.post(fullPath, json.dumps(modelPayload))
        print(resp.status_code)
        if (resp.status_code >= 300):
            print(resp.text)





if __name__ == "__main__":

    HUMAN_JUDGMENTS = './ltr/human_judgments.txt'
    TRAIN_JUDGMENTS = './ltr/train_judgments.txt'
    TEST_JUDGMENTS = './ltr/test_judgments.txt'

    from elasticsearch import Elasticsearch
    from sys import argv
    from ltr.judgments import judgmentsFromFile, judgmentsByQid, duplicateJudgmentsByWeight
    from time import sleep
    from ltr.load_features import init_store, load_features, save_model

    es_host='http://localhost:9200'
    es = Elasticsearch(timeout=1000)

    init_store(es_host)
    sleep(1)
    load_features(es_host)

    # Parse a judgments
    docs_judgments = judgmentsByQid(judgmentsFromFile(filename=HUMAN_JUDGMENTS))
    docs_judgments = duplicateJudgmentsByWeight(docs_judgments)
    trainJudgments, testJudgments = partitionJudgments(docs_judgments, testProportion=0.5)

    # Use proposed Elasticsearch queries (1.json.jinja ... N.json.jinja) to generate a training set
    # output as "sample_judgments_wfeatures.txt"
    log_features(es, judgmentsByQid=docs_judgments)

    build_train_file(trainJudgments, filename=TRAIN_JUDGMENTS)
    build_train_file(testJudgments, filename=TEST_JUDGMENTS)

    # Train each ranklib model type
    # for modelType in [8,9,6]: incluir múltiplos modelos para serem escolhidos dps
    print("Training")
    # train here
    save_model(es_host, feature_set="m05")
