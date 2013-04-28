import os
import random
import sys

import snap as Snap
import swlib

#distmean = 150
#distvar  = 22.5
distmean = 8.0
#distmean = 3
distvar  = 1.0

def GenStubs(sw):
    """
    determine degrees for all the nodes, generate the stubs and distribute them
    """

    taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.log.debug("msglist " + str(msglist))

    ntasks = int(sw.GetVar("gen_tasks"))
    sw.log.debug("__tasks__ %s\t%s" % (taskname, str(ntasks)))

    for item in msglist:
        dmsg = sw.GetMsg(item)
        d = dmsg["body"]
        sw.log.debug("task %s, args %s" % (taskname, str(d)))

        ns = d["s"]
        nrange = d["r"]

        sw.log.debug("task %s, start %d, range %d" % (taskname, ns, nrange))

        # determine node degrees
        DegV = Snap.TIntV(nrange)
        Snap.GetDegrees(DegV,distmean,distvar)

        sw.log.debug("1: got degrees")

        # randomly assign stubs to tasks
        Tasks = Snap.TIntIntVV(ntasks)
        Snap.AssignRndTask(DegV, Tasks)

        sw.log.debug("2: assigned stubs")

        # add ns to all values in Tasks
        for i in range(0,Tasks.Len()):
            Snap.IncVal(Tasks.GetVal(i), ns)

        sw.log.debug("3: incremented base")

        # send messages
        for i in range(0,Tasks.Len()):
            sw.log.debug("sending task %d, len %d" % \
                    (i, Tasks.GetVal(i).Len()))
            sw.Send(i,Tasks.GetVal(i),swsnap=True)

def Worker(sw):
    GenStubs(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    fname = "log-swwork-%s.txt" % (sw.GetName())

    sw.SetLog(fname)
    sw.GetConfig()

    Snap.SeedRandom()
    Worker(sw)

    sw.log.debug("finished")

