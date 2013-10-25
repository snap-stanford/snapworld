import os
import sys
import numpy as np
from sklearn.gaussian_process import GaussianProcess

config_para = None
system_info = None

def load_log():
	global config_para
	global system_info
	config_para = data_io.read_cosfig_parameter()
	system_info = data_io.read_system_infomation()

def normalize(x, y, l1):
	for i in range(x):
		for j in range(x[i]):
			if (j in l1):
				x[i][j] /= y
	return x

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

if __name__ == '__main__':
		