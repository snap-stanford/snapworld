import os
import gatekeeperlib

pid = os.getpid()

#for i in xrange(0,4000):
for i in xrange(0,20000):

    if i % 1000 == 0:
        print "__pid__",pid, i

    gk = gatekeeperlib.GateKeeperClient("localhost",1234)

    count = 0
    while count < 1:

        count += 1
        if count % 1000 == 0:
            #print i, count
            pass

        result = gk.acquire("net","123",123456)
        if not result:
            print "*** Error *** acquire", pid, i, count

    gk.close()

