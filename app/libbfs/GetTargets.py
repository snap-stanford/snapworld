import os
import random
import sys
import traceback

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

def main():
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    fname = "swwork-%s.log" % (sw.GetName())

    sw.SetLog(fname)
    sw.GetConfig()

    Worker(sw)

    sw.log.info("finished")

if __name__ == '__main__':
    try:
        main()
    except:
        sys.stdout.write("[ERROR] Exception in GetTargets.main()\n")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(2)

