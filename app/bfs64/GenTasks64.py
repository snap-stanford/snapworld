import sys
import traceback

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
    
    for ns in xrange(0,nnodes,tsize):
        tname = ns / tsize  # Task-N, tname = N
        ne = min(ns + tsize, nnodes)     # num ending (exclude)

        dout = {}
        dout["s"] = ns      # start, inclusive
        dout["r"] = ne-ns   # range, inclusive of start

        dmsgout = {}
        dmsgout["src"] = taskname
        dmsgout["cmd"] = "nodes"
        dmsgout["body"] = dout

        sw.Send(tname, dmsgout)

def Worker(sw):
    GenTasks(sw)

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
        sys.stdout.write("[ERROR] Exception in GenTasks.main()\n")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(2)

