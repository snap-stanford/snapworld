import httplib
import os, sys
import socket
import time
import urllib2
import urllib
import logging
import json
import threading

import config
from generate_feature import generate_features
from parameter_training import Train
from parameter_predict import predict

Snap = None

def getkv(server):
    url = "http://%s/getkv" % (server)
    f = urllib2.urlopen(url)
    kv_file = f.read()
    f.close()
    return kv_file

def message(server, src, dst, body):
    # send a task message from src to dst
    url = "http://%s/msg/%s/%s" % (server,dst,src)
    length = len(body)

    # print "message url", url

    request = urllib2.Request(url, data=body)
    request.add_header('Content-Length', '%d' % length)
    f = urllib2.urlopen(request)
    body = f.read()
    f.close()

def poll_for_kv(data, server_list, master_server):
    not_done = True
    while not_done:
        for server in server_list:
            try:
                output = getkv(server)
                if len(output) > 4:
                    if output.startswith("DONE") and server == master_server:
                        output = output[5:]
                        not_done = False
                    data[server] = json.loads(output)
                time.sleep(1)
            except (socket.error, urllib2.URLError) as e:
                logging.warning('Encountered a socket error when connecting to %s. Retrying...' % server)
                time.sleep(4)
    for server in server_list:
        if server != master_server:
            output = getkv(server)
            if len(output) > 4:
                data[server] = json.loads(output)
    return data

def get_servers():
    """
    Returns (master host, list of supervisors and master)
    """
    servers = []
    conf = config.readconfig('snapw.config')
    master = conf["master"]["host"] + ":" + conf["master"]["port"]
    servers.append(master)
    for supervisor in conf["hosts"]:
        servers.append(supervisor["host"] + ":" + supervisor["port"])

    return master, servers



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')
    
    data = {}
    config_path = 'snapw.config'
    conf = config.readconfig(config_path)
    # server_list = ['ild1.stanford.edu:9200', 'ild1.stanford.edu:9201', 'ild2.stanford.edu:9201']
    master_server, server_list = get_servers()
    data_c = threading.Thread(target=poll_for_kv, args=(data, server_list, master_server ))
    data_c.start()
    while data_c.isAlive():
        time.sleep(1)
    print "Learning data captured."
    # Conf is a dictionary with key as paramter, value as value, i.e. k-v file,
    # Data is dictionary with key as machine, value as the k-k-v file, 
    # setting is a dictionary with key as parameter, value as the category,
    # features, target = generate_features(conf, data, setting)
    # Train(features, target)
    # new_conf_d = predict(features)
    # Generate new configuration file and pass to other machines.
    print v
        
