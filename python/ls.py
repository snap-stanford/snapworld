import httplib
import os, sys
import socket
import time
import urllib2
import urllib
import logging
import json
import threading
import subprocess
import shlex

import config
from generate_feature import generate_features
from parameter_training import train
from parameter_predict import predict

Snap = None

def getkv(server):
    url = "http://%s/getkv" % (server)
    f = urllib2.urlopen(url)
    kv_file = f.read()
    f.close()
    return kv_file

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
    try:
        for server in server_list:
            if server != master_server:
                output = getkv(server)
                if len(output) > 4:
                    data[server] = json.loads(output)
    except e:
        logging.error(e)
    print data
    logging.info("Thread finished polling")

def send_conf_file(conf_file, server):
    # sends the configuration file to some server via scp
    # Create file first
    fname = "/tmp/conf_%d" % (int(time.time()))
    user = os.environ["USER"]
    with open(fname, 'w') as f:
        f.write(json.dumps(conf_file))
    
    cmd = "scp %s@%s:%s %s@%s:%s" % (user, os.environ["HOSTNAME"], fname, user, server, fname)
    logging.info("Sending file over")
    return subprocess.call(shlex.split(cmd))

def check_conf_file(server):
    now = int(time.time())
    url = "http://%s/hasnewconf/%d" % (server, now)
    f = urllib2.urlopen(url)
    ts = int(f.read())
    f.close()
    if ts > now:
        return True
    return False


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

def learning_pipeline(data, conf, config_path='snapw.config'):
    master_server, server_list = get_servers()
    data_c = threading.Thread(target=poll_for_kv, args=(data, server_list, master_server ))
    data_c.start()
    while data_c.isAlive():
        time.sleep(1)
    logging.info("Learning data captured.")
    # Conf is a dictionary with key as paramter, value as value, i.e. k-v file.
    # Data is dictionary with key as machine, value as the k-k-v file.
    # Setting is a dictionary with key as parameter, value as the category.
    logging.critical("DATA: %s", data)
    label_rt = 1.0
    setting = {"GenTasks": "average", "GenStubs":"average", "GenGraph":"average", "GetNbr":"average"}

    logging.info("Generating features.")
    features, target = generate_features(label_rt, conf["var"], data, setting)
    logging.info("Training model.")
    train(features, target)
    logging.info("Generating new configuration file")
    new_conf_d = predict(conf["var"])
    return new_conf_d
    


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')
    
    data = {}
    config_path = 'snapw.config'
    conf = config.readconfig(config_path)
    master_server = get_servers()[0].split(":")[0]
    # server_list = ['ild1.stanford.edu:9200', 'ild1.stanford.edu:9201', 'ild2.stanford.edu:9201']
    new_conf = learning_pipeline(data, conf)
    logging.info("New Config file: %s" % new_conf)
    send_conf_file(new_conf, master_server)
    time.sleep(3)
    # TODO(nkhadke): Test.
    #print check_conf_file(master_server)
