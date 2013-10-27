import os
import sys
import collection
import numpy as np
from sklearn.gaussian_process import GaussianProcess


config_para = None
system_info = None

def load_log():
	global config_para
	global system_info
	config_para = data_io.read_cosfig_parameter()
	system_info = data_io.read_system_infomation()

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

def make_string(x, label):
	feature_map_input = open(data_io.read_feature_map(), "r")
	feature_map = dict()
	maxn = 0
	try:
		for line in feature_map_input:
			feature_map[line.split(",")[0]] = int(line.split(",")[1])
			if (int(line.split(",")[1]) > maxn):
				maxn = int(line.split(",")[1])
	finally:
		feature_map_input.close()

	tmp = dict()
	for key in x:
		if key in feature_map:
			tmp[feature_map[key]] = x[key]
		else
			maxn += 1
			feature_map[key] = maxn
			tmp[feature_map[key]] = x[key]

	tmp = collections.OrderedDict(sorted(tmp.items()))

	ret = str(label)
	for key in tmp:
		ret = ret + " " + str(key) + ":" + str(tmp[key])

	feature_map_output = open(data_io.read_feature_map(), "w")
	try:
		for key in feature_map:
			feature_map_output.write(key + "," + feature_map[key])
	finally:
		feature_map_output.close()
	
	return ret

def generate_features(conf, data, setting):
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
		elif:
			instance[key] = average(data[key])

	st = make_string(instance)
	data = open(data_io.read_train_svm(), "a")
	try:
		data.write(st)
	finally:
		data.close()
	
	return Load_data_svm()


if __name__ == '__main__':
	generate_features()
