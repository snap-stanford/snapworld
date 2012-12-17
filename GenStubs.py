import os
import random
import sys

import swlib

#distmean = 150
#distvar  = 22.5
distmean = 8
#distmean = 3
distvar  = 1

def StdDist(mean,dev):
    x = 0.0
    for i in range(0,12):
        x += random.random()

    x -= 6.0
    x *= dev
    x += mean

    return int(x + 0.5)

def GenStubs(sw):
    """
    determine degrees for all the nodes, generate the stubs and distribute them
    """

    taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.flog.write("msglist " + str(msglist) + "\n")
    sw.flog.flush()

    for item in msglist:
        dmsg = sw.GetMsg(item)
        d = dmsg["body"]
        sw.flog.write("task %s, args %s\n" % (taskname, str(d)))
        sw.flog.flush()

        ns = d["s"]
        ne = ns + d["r"]

        sw.flog.write("task %s, start %d, end %d\n" % (taskname, ns, ne))
        sw.flog.flush()

        # determine node degrees
        i = ns
        ddeg = {}
        while i <= ne:
            deg = StdDist(distmean,distvar)
            #deg = 3
            ddeg[i] = deg
            sw.flog.write("task %s, node %s, degree %s\n" % (taskname, str(i), str(deg)))
            sw.flog.flush()
            i += 1

    sw.flog.write("ddeg " + str(ddeg) + "\n")
    sw.flog.flush()

    # distribute the stubs randomly to the tasks
    ntasks = int(sw.GetVar("gen_tasks"))
    sw.flog.write("__tasks__ %s\t%s\n" % (taskname, str(ntasks)))
    sw.flog.flush()

    # each task has a list of stubs
    dstubs = {}
    for key,value in ddeg.iteritems():
        for i in range(0,value):
            t = int(random.random() * ntasks)
            if not dstubs.has_key(t):
                dstubs[t] = []
            dstubs[t].append(key)

    sw.flog.write("dstubs " + str(dstubs) + "\n")
    sw.flog.flush()

    dmsgout = {}
    dmsgout["src"] = taskname
    dmsgout["cmd"] = "stubs"

    for tdst, msgout in dstubs.iteritems():
        sw.flog.write("sending task %d, msg %s" % (tdst, str(msgout)) + "\n")
        sw.flog.flush()
        dmsgout["body"] = msgout
        sw.Send(tdst, dmsgout)

def Worker(sw):
    GenStubs(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    #flog = sys.stdout
    fname = "log-swwork-%s.txt" % (sw.GetName())
    flog = open(fname,"a")

    sw.SetLog(flog)
    sw.GetConfig()

    Worker(sw)

    flog.write("finished\n")
    flog.flush()

