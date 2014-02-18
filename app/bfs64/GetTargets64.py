import random
import sys
import traceback

import swlib

# TODO (smacke): Here we are taking a single source node from which
# to BFS, but the legacy naming scheme makes it seem like there
# should be nsample source nodes. Furthermore, we don't seem
# to be using the nsample variable except for logging.

# Eventually we'll want to make partitioned GetDist work
# for more than just a single source node.
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
    # TODO (smacke): debug only
    random.seed(0)
    n = int(random.random() * nnodes)

    for ns in xrange(0, nnodes, tsize):
        tname = ns / tsize
        ne = min(ns+tsize, nnodes)

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

