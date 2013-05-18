import httplib
import random
import os
import socket
import sys
import time
import urllib2
import mmap
import traceback

def SendVec(server, src, dst, fname):
    f = open(fname, "rb")
    mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)

    h = httplib.HTTPConnection(server)

    wait_time = 1
    for i in range(0,8):
        swok = False
        try:
            h.connect()
            swok = True
        except socket.error, e:
            # check out for socket.error:
            # [Errno 110] Connection timed out
            # [Errno 111] Connection refused
            if e.errno != 110 and e.errno != 111:
                # break out of the loop and fail later
                swok = True

        if swok:
            break

        # TODO: log errors that are not due to timeouts.
        wait_time *= 2
        # Exponential Backoff
        sleeptime = wait_time
        print "BACKOFF for", sleeptime
        sys.stdout.flush()
        time.sleep(sleeptime)

    left = mm.size()

    url = "/msg/%s/%s" % (dst,src)
    # print url
    h.putrequest("POST",url)
    h.putheader("Content-Length", str(left))
    h.endheaders()

    fileno = h.sock.fileno()

    while left > 0:
        nbytes = min(102400, left)
        data = mm.read(nbytes)
        while nbytes > 0:
            # error: [Errno 104] Connection reset by peer; in send()
            nsent = h.sock.send(data)
            if nsent != nbytes:
                print "OOPS: sent: %d, expected: %d" % (nsent, nbytes)
            nbytes -= nsent
            left -= nsent
            data = data[nsent:]

    res = h.getresponse()
    # print res.status, res.reason

    data = res.read()

    h.close()


def main():

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " -hp <host:port> -f <file>"
        sys.exit(1)

    hostport = None
    fname = None

    index = 1
    while index < len(sys.argv):
        arg = sys.argv[index]
        if arg == "-hp":
            index += 1
            hostport = sys.argv[index]
        elif arg == "-f":
            index += 1
            fname = sys.argv[index]

        index += 1

    pid = "%6d " % os.getpid()

    start_time = time.time()
    
    src = "TaskA-%d" % (int(random.random()*500))
    SendVec(hostport,src,"TaskA-0", fname)

    time_taken = time.time() - start_time
    print "pid", pid, "time_taken", time_taken, "done"

if __name__ == '__main__':

    sent = False
    while not sent:
        try:
            main()
            sent = True
        except:
            print "ERROR: %d" % os.getpid()
            traceback.print_exc()
            sys.stdout.flush()
            sys.stderr.flush()

