import httplib
import os
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
    h.connect()
    url = "/msg/%s/%s" % (dst,src)
    h.putrequest("POST",url)
    h.putheader("Content-Length", str(Vec.GetMemSize()))
    h.endheaders()

    fileno = h.sock.fileno()
    #print "fileno", fileno

    n = Vec.Send(fileno)
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

    print "port", port
    print "length", length
    print "file", fname

    host = "127.0.0.1:%s" % (port)
    print "host", host

    if not fname:
        print time.ctime(), "generating vector with %d elements ..." % (length)
        Vec = CreateVec(length)
    else:
        print time.ctime(), "reading file %s ..." % (fname)
        Vec = ReadVec(fname)

    print time.ctime(), "sending vector with %d elements, size %.1fMb ..." % (Vec.Len(), float(Vec.GetMemSize())/1000000.0)
    SendVec(host,"TaskA-0","TaskA-0",Vec)

    print time.ctime(), "done"

