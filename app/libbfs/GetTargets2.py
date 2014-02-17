import random
import sys
import traceback

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

    sw.log.info("task: %s, nodes: %d, tsize: %d" % (nnodes, nsample, tsize))

    # select the single source node
    # TODO (smacke): for debug only
    random.seed(0)
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
        dmsgout["src"] = sw.GetName()
        dmsgout["cmd"] = "nodes"
        dmsgout["body"] = dout

        sw.Send(tname, dmsgout)

        ns = ne

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
        sys.stdout.write("[ERROR] Exception in GetTargets2.main()\n")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(2)

