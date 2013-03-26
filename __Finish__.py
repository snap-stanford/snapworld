import os
import random
import sys

import swlib

#workdir = "/home/rok"

workdir = os.environ["SNAPWOUTPUT"]

def Finish(sw):
    """
    receive the final results
    """

    msglist = sw.GetMsgList()
    sw.flog.write("msglist " + str(msglist) + "\n")
    sw.flog.flush()

    # get the results
    GetResults(msglist)

def GetResults(msglist):

    for item in msglist:
        dmsg = sw.GetMsg(item)
        msg = dmsg["body"]

        start = msg["start"]
        dist = msg["dist"]

        #print edges
        sw.flog.write("node %s, distances %s\n" % (start, str(dist)))
        sw.flog.flush()

def Worker(sw):
    Finish(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    pid = os.getpid()

    fname = "log-swfinish-%d.txt" % (pid)
    #fname = "log-swwork-%s.txt" % (sw.GetName())
    fullname = os.path.join(workdir,fname)
    flog = open(fullname,"a")

    sw.SetLog(flog)
    sw.GetConfig()

    Worker(sw)

    flog.write("finished\n")
    flog.flush()

