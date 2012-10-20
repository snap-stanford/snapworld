import os
import sys

import swlib

def GenTasks(sw):
    """
    generate the tasks
    """

    taskname = sw.GetName()

    # total number of nodes
    nnodes = int(sw.GetVar("nodes"))

    # nodes in each task
    tsize = sw.GetRange()

    sw.flog.write("task %s, nodes %d, tsize %d\n" % (taskname, nnodes, tsize))
    sw.flog.flush()

    ns = 0
    while ns < nnodes:
        tname = ns / tsize
        ne = ns + tsize
        if ne > nnodes:
            ne = nnodes

        dout = {}
        dout["s"] = ns
        dout["r"] = ne-ns

        sw.Send(tname, dout)

        ns = ne

def Worker(sw):
    GenTasks(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    #flog = sys.stdout
    fname = "log-swwork-%s.txt" % (sw.GetName())
    flog = open(fname,"w")

    sw.SetLog(flog)
    sw.GetConfig()

    Worker(sw)

    flog.write("finished\n")
    flog.flush()

