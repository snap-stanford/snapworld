import os
import random
import sys

import swlib

def SelectNodes(sw):
    """
    select random nodes for distance calculations
    """

    # total number of nodes
    nnodes = int(sw.GetVar("nodes"))

    # number of distance task partitions
    nsample = int(sw.GetVar("stat_tasks"))

    # nodes in each partition
    tsize = sw.GetRange()

    sw.flog.write("task %s, nodes %d, tsize %d\n" % (nnodes, nsample, tsize))
    sw.flog.flush()

    # select the single source node
    n = int(random.random() * nnodes)

    ns = 0
    while ns < nnodes:
        tname = ns / tsize
        ne = ns + tsize
        if ne > nnodes:
            ne = nnodes

        dout = {}
        dout["s"] = ns
        dout["r"] = ne-ns
        if n >= ns  and  n < ne:
            dout["source"] = n

        dmsgout = {}
        dmsgout["src"] = taskname
        dmsgout["cmd"] = "nodes"
        dmsgout["body"] = dout

        sw.Send(tname, dmsgout)

        ns = ne

def Worker(sw):
    SelectNodes(sw)

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

