import httplib
import os
import random
import socket
import time
import urllib2
import urllib
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')

Snap = None

def config(server):
    # get configuration
    url = "http://%s/config" % (server)
    f = urllib2.urlopen(url)
    sconf = f.read()
    f.close()

    return sconf

def step(server):
    # send step start
    url = "http://%s/step" % (server)

    #print "step", server

    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

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

def quit(server):
    # send termination quit
    url = "http://%s/quit" % (server)

    #print "step", server

    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

def dummy(server):
    # send a dummy request
    url = "http://%s/dummy" % (server)

    #print "step", server

    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

def prepare(server):
    # send step prepare
    url = "http://%s/prepare" % (server)

    #print "step", server

    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

def done(server, id):
    # send done
    url = "http://%s/done/%s" % (server,id)
    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

def ready(server, id, numtasks=0):
    # send ready
    url = "http://%s/ready/%s/%s" % (server,id,str(numtasks))
    f = urllib2.urlopen(url)
    body = f.read()
    f.close()

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

def messagevec(server, src, dst, Vec):
    global Snap

    h = httplib.HTTPConnection(server)
    
    wait_time = 1
    for i in range(0,8):
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
            else:
                logging.critical("socket.error: %s" % str(e))
                # break out of the loop and fail later
                sw_ok = True
        if sw_ok: break

        time.sleep(wait_time)
        wait_time *= 2 # Exponential Backoff 

    context_length = Vec.GetMemSize()
    logging.debug("messagevec context-length: %d" % context_length)

    url = "/msg/%s/%s" % (dst, src)
    h.putrequest("POST", url)
    h.putheader("Content-Length", str(context_length))
    h.endheaders()

    fileno = h.sock.fileno()

    if Snap is None:
        import snap as Snap
    r = Snap.SendVec_TIntV(Vec, fileno)
    if r < 0:
        logging.critical("Snap.SendVec_TIntV returned with error %d" % r)
        h.close()
        raise Exception("Snap.SendVec_TIntV error %d" % r)

    res = h.getresponse()
    #print res.status, res.reason

    data = res.read()

    h.close()

def error(server, src_id, msg):
    encoded_msg = urllib.urlencode({ 'msg': str(msg) })
    url = "http://%s/error/%s/%s" % (str(server), str(src_id), encoded_msg)
    f = urllib2.urlopen(url)
    body = f.read()
    f.close()
