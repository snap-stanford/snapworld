import os
import sys
import csv
import json
import pickle
import pandas as pd
from operator import itemgetter

def get_paths():
    # TODO (smacke): This is very baddddddddddd
    path = "/afs/cs.stanford.edu/u/%s/hanworks/snapworld/python/settings.json" % os.environ["USER"]
    paths = None
    with open(path) as f:
        paths = json.loads(f.read())
        for key in paths:
            paths[key] = os.path.expandvars(paths[key])
    return paths

def read_train_csv():
    train_path = get_paths()["train_path_csv"]
    return pd.read_csv(train_path)

def read_test_csv():
    test_path = get_paths()["test_path_csv"]
    return pd.read_csv(test_path)

def read_train_svm():
    train_path = get_paths()["train_path_svm"]
    return train_path

def read_test_svm():
    train_path = get_paths()["test_path_svm"]
    return train_path

def save_model(model):
    out_path = get_paths()["model_path"]
    pickle.dump(model, open(out_path, "w"))

def load_model():
    in_path = get_paths()["model_path"]
    return pickle.load(open(in_path))

def feature_map():
    feature_map = get_paths()["feature_map"]
    return feature_map
