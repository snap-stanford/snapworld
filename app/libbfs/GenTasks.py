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

    sw.log.debug("task %s, nodes %d, tsize %d" % (taskname, nnodes, tsize))
    
    ns = 0
    while ns < nnodes:
        tname = ns / tsize
        ne = ns + tsize
        if ne > nnodes:
            ne = nnodes

        dout = {}
        dout["s"] = ns
        dout["r"] = ne-ns

        dmsgout = {}
        dmsgout["src"] = taskname
        dmsgout["cmd"] = "nodes"
        dmsgout["body"] = dout

        sw.Send(tname, dmsgout)

        ns = ne

def Worker(sw):
    GenTasks(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    fname = "swwork-%s.log" % (sw.GetName())
    
    sw.SetLog(fname)
    sw.GetConfig()

    Worker(sw)

    sw.log.info("finished")

