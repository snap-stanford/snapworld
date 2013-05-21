import httplib
import os, sys
import socket
import time
import urllib2
import urllib
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')

Snap = None

def socket_retry(func):
    def inner_func(*args, **kwargs):
        wait_time = 1
        for i in xrange(7):
            try:
                return func(*args, **kwargs)
            except socket.error as e:
                logging.warn("socket_retry; attempt: %d; msg: %s" % (i, str(e)))
                time.sleep(wait_time)
                wait_time *= 2 # Exponential Backoff
        logging.error("socket_retry failed")
        sys.exit(2)
    return inner_func

@socket_retry
def config(server):
    # get configuration
    url = "http://%s/config" % (server)
    f = urllib2.urlopen(url)
    sconf = f.read()
    f.close()

    return sconf

@socket_retry
def step(server):
    # send step start
    url = "http://%s/step" % (server)

    #print "step", server

    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

@socket_retry
def getexec(server,prog,timestamp):
    '''
    get executable from the head task
    - return values
        "", no change
        <body>, new content
        None, no file found
    '''

    # send a request for executable
    if not timestamp:
        url = "http://%s/exec?p=%s" % (server, prog)
    else:
        url = "http://%s/exec?p=%s&t=%s" % (server, prog, str(timestamp))

    # print "exec", server, prog, timestamp

    httpcode = 200
    try:
        f = urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        httpcode = e.code

    if httpcode == 304:
        return ""

    if httpcode != 200:
        return None

    body = f.read()
    f.close()

    return body

@socket_retry
def quit(server):
    # send termination quit
    url = "http://%s/quit" % (server)

    #print "step", server

    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

@socket_retry
def dummy(server):
    # send a dummy request
    url = "http://%s/dummy" % (server)

    #print "step", server

    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

@socket_retry
def prepare(server):
    # send step prepare
    url = "http://%s/prepare" % (server)

    #print "step", server

    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

@socket_retry
def done(server, id):
    # send done
    url = "http://%s/done/%s" % (server,id)
    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

@socket_retry
def ready(server, id, numtasks=0):
    # send ready
    url = "http://%s/ready/%s/%s" % (server,id,str(numtasks))
    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

@socket_retry
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

@socket_retry
def messagevec(server, src, dst, Vec):
    global Snap

    content_length = Vec.GetMemSize()
    
    # need_token = (content_length >= 1*1024*1024)
    need_token = True

    if need_token: acquire_token()

    h = httplib.HTTPConnection(server)
    
    wait_time = 1
    for i in xrange(8):
        sw_ok = False
        try:
            h.connect()
            sw_ok = True
        except socket.error, e:
            # check out for socket.error: [Errno 110] Connection timed out
            if e.errno == 110:
                logging.warn("[Error 110] Connection timed out; attempt: %d, dest: %s" % (i, str(dst)))
            elif e.errno == 111:
                logging.warn("[Errno 111] Connection refused; attempt: %d, dest: %s" % (i, str(dst)))
            elif e.errno == -2:
                logging.warn("[Errno -2] Name or service not know: attempt: %d, dest: %s" % (i, str(dst)))
            else:
                logging.critical("socket.error: %s: attempt: %d, dest: %s" % (str(e), i, str(dst)))
                # break out of the loop and fail later
                sw_ok = True
        if sw_ok: break

        time.sleep(wait_time)
        wait_time *= 2 # Exponential Backoff 

    if not sw_ok:
        logging.critical("Could not establish connection to dest: %s" % str(dst))
        if need_token: release_token()
        sys.exit(2)

    logging.debug("messagevec content-length: %d" % content_length)

    url = "/msg/%s/%s" % (dst, src)
    h.putrequest("POST", url)
    h.putheader("Content-Length", str(content_length))
    h.endheaders()

    fileno = h.sock.fileno()

    if Snap is None:
        import snap as Snap
    r = Snap.SendVec_TIntV(Vec, fileno)
    if r < 0:
        logging.warn("Snap.SendVec_TIntV returned with error %d" % r)
        h.close()
        if need_token: release_token()
        raise socket.error("Send.SendVec_TIntV error")

    res = h.getresponse()
    #print res.status, res.reason

    data = res.read()

    h.close()

    if need_token: release_token()

@socket_retry
def error(server, src_id, msg):
    encoded_msg = urllib.urlencode({ 'msg': str(msg) })
    url = "http://%s/error/%s/%s" % (str(server), str(src_id), encoded_msg)
    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

def acquire_token():
    broker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pid = os.getpid()
    try:
        broker_sock.connect(("127.0.0.1", 1337))
        acq_cmd = "acquire|net|%d\n" % pid
        broker_sock.send(acq_cmd)
        rv = broker_sock.recv(1024).strip()
        if rv == "ACQUIRED":
            logging.info("Worker %d acquired token" % pid)
        else:
            logging.critical("Error in acquiring token from broker")
            broker_sock.close()
            sys.exit(2)
        broker_sock.close()
    except socket.error, (value,message):
        logging.critical("Error in connecting to broker: %s" % message)
        broker_sock.close()
        sys.exit(2)


def release_token():
    broker_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pid = os.getpid()
    try:
        broker_sock.connect(("127.0.0.1", 1337))
        rel_cmd = "release|net|%d\n" % pid
        broker_sock.send(rel_cmd)
        rv = broker_sock.recv(1024).strip()
        if rv == "RELEASED":
            logging.info("Worker %d released token" % pid)
        else:
            logging.critical("Error in releasing token to broker")
            broker_sock.close()
            sys.exit(2)
        broker_sock.close()
    except socket.error, (value,message):
        logging.critical("Error in connecting to broker: %s" % message)
        broker_sock.close()
        sys.exit(2)

