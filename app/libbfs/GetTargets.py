import os
import random
import sys

import swlib

def SelectNodes(sw):
    """
    select random nodes for distance calculations
    """

    # get all the nodes and the number of samples
    nnodes = int(sw.GetVar("nodes"))
    nsample = int(sw.GetVar("stat_tasks"))

    s = set()
    for i in range(0, nsample):

        while 1:
            n = int(random.random() * nnodes)
            if not n in s:
                break

        dmsgout = {}
        dmsgout["src"] = sw.GetName()
        dmsgout["cmd"] = "target"
        dmsgout["body"] = n

        sw.Send(i,dmsgout)

        s.add(n)

def Worker(sw):
    SelectNodes(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    fname = "log-swwork-%s.txt" % (sw.GetName())

    sw.SetLog(fname)
    sw.GetConfig()

    Worker(sw)

    sw.log.info("finished")

