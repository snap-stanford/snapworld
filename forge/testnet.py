import httplib
import random
import os
import socket
import sys
import time
import urllib2

import snap as Snap

def CreateVec(length):
    Vec = Snap.TIntV()
    for i in xrange(0,length):
        value = (i*3) % 1000
        Vec.Add(value)

    return Vec

def ReadVec(fname):
    FIn = Snap.TFIn(Snap.TStr(fname))
    Vec = Snap.TIntV(FIn)
    return Vec

def SendVec(server, src, dst, Vec):
    h = httplib.HTTPConnection(server)
    for i in range(0,10):
        swok = False
        try:
            h.connect()
            swok = True
        except socket.error, e:
            # check out for socket.error: [Errno 110] Connection timed out
            if e.errno != 110:
                # break out of the loop and fail later
                swok = True

        if swok:
            break

        pid = "%6d " % os.getpid()
        print pid, time.ctime(), "*** ERROR *** retry ", i
        sleeptime = random.random()*10 + 5
        time.sleep(sleeptime)

    #Traceback (most recent call last):
    #  File "testnet.py", line 85, in <module>
    #    SendVec(host,"TaskA-0","TaskA-0",Vec)
    #  File "testnet.py", line 24, in SendVec
    #    h.connect()
    #  File "/usr/lib64/python2.6/httplib.py", line 720, in connect
    #    self.timeout)
    #  File "/usr/lib64/python2.6/socket.py", line 567, in create_connection
    #    raise error, msg
    #socket.error: [Errno 110] Connection timed out

    url = "/msg/%s/%s" % (dst,src)
    h.putrequest("POST",url)
    h.putheader("Content-Length", str(Vec.GetMemSize()))
    h.endheaders()

    fileno = h.sock.fileno()
    #print "fileno", fileno

    n = Snap.SendVec_TIntV(Vec, fileno)
    #print n

    res = h.getresponse()
    #print res.status, res.reason
    data = res.read()
    #print len(data)
    #print data

    h.close()

if __name__ == '__main__':

    if len(sys.argv) < 5:
        print "Usage: " + sys.argv[0] + " -p <port> [ -g <length> | -f <file>"
        sys.exit(1)

    port = 80
    length = 1000
    fname = None

    index = 1
    while index < len(sys.argv):
        arg = sys.argv[index]
        if arg == "-p":
            index += 1
            port = sys.argv[index]
        elif arg == "-g":
            index += 1
            length = int(sys.argv[index])
        elif arg == "-f":
            index += 1
            fname = sys.argv[index]

        index += 1

    #print "port", port
    #print "length", length
    #print "file", fname

    host = "127.0.0.1:%s" % (port)
    #print "host", host

    pid = "%6d " % os.getpid()

    if not fname:
        print pid, "generating %d elements ..." % (length)
        sys.stdout.flush()
        Vec = CreateVec(length)
    else:
        print pid, time.ctime(), "reading file %s ..." % (fname)
        sys.stdout.flush()
        Vec = ReadVec(fname)

    print pid, time.ctime(), "sending %d elements, size %.1fMb ..." % (Vec.Len(), float(Vec.GetMemSize())/1000000.0)
    sys.stdout.flush()
    src = "TaskA-%d" % (int(random.random()*500))
    SendVec(host,src,"TaskA-0",Vec)

    print pid, time.ctime(), "done"
    sys.stdout.flush()


