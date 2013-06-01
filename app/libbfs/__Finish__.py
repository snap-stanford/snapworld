import os
import sys

import swlib

#workdir = "/home/rok"

workdir = os.environ["SNAPW_OUTPUT"]

def Finish(sw):
    """
    receive the final results
    """

    msglist = sw.GetMsgList()
    sw.log.debug("msglist %s" % str(msglist))

    # get the results
    GetResults(msglist)

def GetResults(msglist):

    for item in msglist:
        dmsg = sw.GetMsg(item)
        msg = dmsg["body"]

        start = msg["start"]
        dist = msg["dist"]

        sw.log.info("node %s, distances %s" % (start, str(dist)))

def Worker(sw):
    Finish(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    pid = os.getpid()

    fname = "log-swfinish-%d.txt" % (pid)
    fullname = os.path.join(workdir,fname)

    sw.SetLog(fullname)
    sw.GetConfig()

    Worker(sw)

    sw.log.info("finished")

