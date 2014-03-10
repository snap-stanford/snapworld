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

    # TODO (smacke): perhaps it would make more sense to use a numpy
    # random sample function here.
    # e.g. numpy.random.choice with replace=False
    s = set()
    for i in range(0, nsample):

        while 1: # blah. TODO: while True:
            n = int(random.random() * nnodes)
            if not n in s: # if we have not already considered this node in the sample
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

