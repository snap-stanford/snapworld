import os
import sys
import collections

import data_io
import numpy as np

from sklearn.datasets import load_svmlight_file


config_para = None
system_info = None

def load_log():
    global config_para
    global system_info
    config_para = data_io.read_cosfig_parameter()
    system_info = data_io.read_system_infomation()

def average(x):
    ret = 0.0

    for key in x:
        ret += x[key]

    return float(ret) / len(x)

def normalize(x):
    ret = 0
    maxn = -1000000

    for key in x:
        ret += x[key]
        if (x[key] > maxn):
            maxn = x[key]

    if len(x) == 0 or maxn == 0:
        return 0
    else:
        ret = ret / len(x) / maxn

    return ret

def binaryzation(x, y, lower, upper, percent):
    l = []
    for i in range(x):
        l.append(x[i][y])
    l.sort()

    minn = l[len(l) * lower / 100]
    maxn = l[len(l) * upper / 100]

    t = []
    for i in l:
        if (i > minn and i < maxn):
            t.append(i)
    
    del l

    t.sort()
    threshold = t[len(t) * percent / 100]

    for i in range(x):
        if (x[i][y] <= threshold):
            x[i][y] = 0
        else:
            x[i][y] = 1

    return x

def make_string(label, x):

    feature_map = dict()

    # Load feature map
    try:
        feature_map_input = open(data_io.feature_map(), "r")
        for line in feature_map_input:
            feature_map[line.split(":")[0]] = int(line.split(":")[1])
        feature_map_input.close()
    except Exception, e:
        pass
    maxn = len(feature_map)

    # Build feature map and rename features
    tmp = dict()
    for key in x:
        if key in feature_map:
            tmp[feature_map[key]] = x[key]
        else:
            feature_map[key] = maxn
            tmp[feature_map[key]] = x[key]
            maxn += 1


    # Write new feature map
    try:
    	feature_map_output = open(data_io.feature_map(), "w")
        for key in feature_map:
            #print feature_map[key]
            feature_map_output.write(key)
            feature_map_output.write(":")
            feature_map_output.write(str(feature_map[key]))
            feature_map_output.write("\n")
        feature_map_output.close()
    except Exception, e:
    	pass

    ret = str(label)
    for key in sorted(tmp.keys()):
        ret += " "
        ret += str(key)
        ret += ":"
        ret += str(tmp[key])

    return ret

def save_to_train(st):
    data = open(data_io.read_train_svm(), "a")
    try:
        data.write(st + "\n")
        data.close()
    except Exception, e:
    	pass

def load_data_csv():
    print("[INFO] Loading data format data...")
    global train
    
    train = data_io.read_train_csv()
    train.fillna(0, inplace=True)
    train_sample = train.fillna(value=0)
    feature_names = list(train_sample.columns)
    
    feature_names.remove("label")
    
    global features
    global target

    features = train_sample[feature_names].values
    target = train_sample["label"].values
    
def load_data_svm():
    print("[INFO] Loading svm-light format data...")
    global features
    global target
    features, target = load_svmlight_file(data_io.read_train_svm())
    features = features.todense()
    return features, target

def generate_features(label, conf, data, setting):
    instance = conf
    
    for key in data:
        if (key in setting):
            if (setting[key] == "average"):
                instance[key] = average(data[key])
            if (setting[key] == "normalize"):
                instance[key] = normalize(data[key])
            if (setting[key] == "binaryzation"):
                instance[key] = normalize(data[key])
            if (setting[key] == "categorization"):
                instance[key] = categorization(data[key])
        else:
            instance[key] = average(data[key])

    save_to_train(make_string(label, instance))

    return load_data_svm()
    
if __name__ == '__main__':
    generate_features()
