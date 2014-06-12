import httplib
import os, sys
import socket
import time
import urllib2
import urllib
import logging
import random
import httpclient
import gatekeeperlib

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')

Snap = None

MAX_RETRIES = 5

def socket_retry(func):
    def inner_func(*args, **kwargs):
        for i in xrange(MAX_RETRIES):
            try:
                return func(*args, **kwargs)
            except (socket.error, urllib2.URLError) as e:
                if i < MAX_RETRIES-1:
                    # Exponential + Random Backoff
                    wait_time = pow(2.0, i) * (1.0 + random.random()) 
                    logging.warn("socket_retry; attempt: %d; backoff: %f, msg: %s" % (i, wait_time, str(e)))
                    time.sleep(wait_time)
                else:
                    logging.warn("socket_retry; msg: %s" % str(e))

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

    if Snap is None:
        import snap as Snap

    if type(Vec) == Snap.TIntIntVV:
        content_length = Snap.GetMemSize64(Vec)
    elif type(Vec) == Snap.TIntV:
        content_length = Vec.GetMemSize()
    else:
        raise ValueError('send not defined for type %s' % str(type(Vec)))

    # need_token = (content_length >= 1*1024*1024)
    need_token = True

    if need_token:
        acquire_token(content_length)

    try:
        client = httpclient.HTTPClient(*server.split(':'))

        logging.debug("messagevec content-length: %d" % content_length)

        url = "/msg/%s/%s" % (dst, src)
        client.h.putrequest("POST", url)
        client.h.putheader("Content-Length", str(content_length))
        client.h.endheaders()

        fileno = client.h.sock.fileno()

        logging.debug("socket: %s" % client.h.sock)

        if type(Vec) == Snap.TIntV:
            r = Snap.SendVec_TIntV(Vec, fileno)
        elif type(Vec) == Snap.TIntIntVV:
            logging.debug('sending vector TIntIntVV')
            r = Snap.SendVec_TIntIntVV(Vec, fileno)
        else:
            raise ValueError('send not defined for type %s' % str(type(Vec)))

        if r < 0:
            logging.warn("Snap.SendVec_TIntV (or SnedVec_TIntIntVV) returned with error %d" % r)
            raise socket.error("Send.SendVec_TIntV (or SendVec_TIntIntVV) error")

        res = client.h.getresponse()
        #print res.status, res.reason

        data = res.read()

    finally:
        try:
            if client.h.sock is not None:
                client.close()
        finally:
            if need_token:
                release_token()

@socket_retry
def error(server, src_id, msg):
    encoded_msg = urllib.urlencode({ 'msg': str(msg) })
    url = "http://%s/error/%s/%s" % (str(server), str(src_id), encoded_msg)
    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

#@socket_retry
def acquire_token(size=-1):
    # TODO (smacke): Make this dynamic via snapw config file
    gkclient = gatekeeperlib.GateKeeperClient('127.0.0.1', 1337)
    gkclient.acquire('net', os.getpid(), size)
    gkclient.close()


#@socket_retry
def release_token():
    # TODO (smacke): Make this dynamic via snapw config file
    gkclient = gatekeeperlib.GateKeeperClient('127.0.0.1', 1337)
    gkclient.release('net', os.getpid())
    gkclient.close()

