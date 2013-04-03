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
    sw.flog.write("msglist " + str(msglist) + "\n")
    sw.flog.flush()

    ntasks = int(sw.GetVar("gen_tasks"))
    sw.flog.write("__tasks__ %s\t%s\n" % (taskname, str(ntasks)))
    sw.flog.flush()

    for item in msglist:
        dmsg = sw.GetMsg(item)
        d = dmsg["body"]
        sw.flog.write("task %s, args %s\n" % (taskname, str(d)))
        sw.flog.flush()

        ns = d["s"]
        nrange = d["r"]

        sw.flog.write("task %s, start %d, range %d\n" % (taskname, ns, nrange))
        sw.flog.flush()

        # determine node degrees
        DegV = Snap.TIntV(nrange)
        Snap.GetDegrees(DegV,distmean,distvar)

        sw.flog.write("1 got degrees\n")
        sw.flog.flush()

        # randomly assign stubs to tasks
        Tasks = Snap.TIntIntVV(ntasks)
        Snap.AssignRndTask(DegV, Tasks)

        sw.flog.write("2 assigned stubs\n")
        sw.flog.flush()

        # add ns to all values in Tasks
        for i in range(0,Tasks.Len()):
            Snap.IncVal(Tasks.GetVal(i), ns)

        sw.flog.write("3 incremented base\n")
        sw.flog.flush()

        # send messages
        for i in range(0,Tasks.Len()):
            #sw.flog.write("sending task %d" % (i) + "\n")
            sw.flog.write("sending task %d, len %d" %
                                (i, Tasks.GetVal(i).Len()) + "\n")
            sw.flog.flush()
            sw.Send(i,Tasks.GetVal(i),swsnap=True)

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

    Snap.SeedRandom()
    Worker(sw)

    flog.write("finished\n")
    flog.flush()

