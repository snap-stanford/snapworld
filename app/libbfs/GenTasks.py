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
    
    ns = 0 # num start
    while ns < nnodes:
        tname = ns / tsize  # Task-N, tname = N
        ne = ns + tsize     # num ending (exclude)
        if ne > nnodes:
            ne = nnodes

        dout = {}
        dout["s"] = ns      # start, inclusive
        dout["r"] = ne-ns   # range, inclusive of start

        dmsgout = {}
        dmsgout["src"] = taskname
        dmsgout["cmd"] = "nodes"
        dmsgout["body"] = dout

        sw.Send(tname, dmsgout)

        ns = ne             # re-assign

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

