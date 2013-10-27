import os
import sys

from generate_feature import generate_features
from parameter_training import train
from parameter_predict import predict

if __name__ == '__main__':

    # Conf is a dictionary with key as paramter, value as value, i.e. k-v file,
    # Data is dictionary with key as machine, value as the k-k-v file, 
    # setting is a dictionary with key as parameter, value as the category,
    # features, target = generate_features(conf, data, setting)
    # train(features, target)
    # new_conf_d = predict(features)
    # Generate new configuration file and pass to other machines.

    label = 1.0
    conf = {"nodes":10000, "range":1, "stat_tasks":1, "gen_tasks":10000, "drange":10000}
    data = {"GenTasks":{1:2.0, 2:3.0, 4:2.4}, "GenStubs":{"a":1.0, "b":2.0, "c":3}, "GenGraph":{"1":101.0, "2":99.0, "4":2.4}, "GetNbr":{"1":1.0, "2":9.0, "4":1.4}, "GetDist":{"1":101.0, "2":99.0, "3":2.4}}
    setting = {"GenTasks": "average", "GenStubs":"average", "GenGraph":"average", "GetNbr":"average"}

    features, target = generate_features(label, conf, data, setting)
    train(features, target)
    new_conf_d = predict(conf)
    print new_conf_d

'''
route   __Start__       GenTasks
route   GenTasks        GenStubs
route   GenStubs        GenGraph
route   GenGraph        GetNbr
route   GetNbr:1        GetDist
route   GetNbr:2        GetTargets
route   GetTargets      GetDist
route   GetDist:1       GetNbr
route   GetDist:2       __Finish__
'''
