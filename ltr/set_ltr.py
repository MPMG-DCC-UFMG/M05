import os
from ltr.collect_features import log_features, build_train_file
from elasticsearch import Elasticsearch
from sys import argv
from ltr.judgments import judgmentsFromFile, judgmentsByQid, duplicateJudgmentsByWeight
from time import sleep
from ltr.load_features import init_store, load_features, save_model
import xgboost as xgb


def train_model(train, test):

    X_train, y_train, qids = [], [], []
    for qid, judgmentList in train.items():
        qids.append(0)
        for judgment in judgmentList:
            X_train.append(judgment.features)
            y_train.append(judgment.grade)
            qids[-1] += 1

    model = xgb.XGBRanker(
        tree_method='hist',
        booster='gbtree',
        objective='rank:pairwise',
        random_state=42,
        learning_rate=0.1,
        colsample_bytree=0.9,
        eta=0.05,
        max_depth=6,
        n_estimators=110,
        subsample=0.75
    )

    model.fit(X_train, y_train, group=qids, verbose=True) #group=groups,
    model = model.get_booster().get_dump(fmap="./ltr/featmap.txt", dump_format='json')
    with open('./ltr/xgboost_model.json', "w") as output:
        output.write('[' + ','.join(list(model)) + ']')
        output.close()

def partition_judgments(judgments, testProportion=0.5):
    from random import random

    test_judgments = {}
    train_judgments = {}
    for qid, judgment in judgments.items():
        draw = random()
        if draw <= testProportion:
            test_judgments[qid] = judgment
        else:
            train_judgments[qid] = judgment

    return (train_judgments, test_judgments)

if __name__ == "__main__":

    HUMAN_JUDGMENTS = './ltr/human_judgments.txt'
    TRAIN_JUDGMENTS = './ltr/train_judgments.txt'
    TEST_JUDGMENTS = './ltr/test_judgments.txt'


    es_host='http://localhost:9200'
    es = Elasticsearch(timeout=1000)

    init_store(es_host)
    sleep(1)
    load_features(es_host)

    # Parse a judgments
    docs_judgments = judgmentsByQid(judgmentsFromFile(filename=HUMAN_JUDGMENTS))
    docs_judgments = duplicateJudgmentsByWeight(docs_judgments)

    #alterar test proportion
    train_judgments, test_judgments = partition_judgments(docs_judgments, testProportion=0)

    # Use proposed Elasticsearch queries (1.json.jinja ... N.json.jinja) to generate a training set
    # output as "sample_judgments_wfeatures.txt"
    log_features(es, judgmentsByQid=docs_judgments)

    build_train_file(train_judgments, filename=TRAIN_JUDGMENTS)
    build_train_file(test_judgments, filename=TEST_JUDGMENTS)
    print("aqui",list(train_judgments.values())[0][0].features)
    # Train each ranklib model type
    print("Training")
    train_model(train_judgments, train_judgments)
    save_model(es_host, feature_set="m05")
