import sys

import comm

def GenTasks(nnodes, ntasks, dis):
    """
    generate the tasks
        nnodes, number of nodes
        ntasks, number of tasks
        dis, degree distribution
    """

    ns = 0
    tc = 0
    while ns < nnodes:
        tname = str(tc)
        tc += 1
        ne = nnodes*tc / ntasks
        tinfo = "%s %d %d %s" % (tname, ns, ne-1, dis)
        print tinfo
        ns = ne
        comm.msend("task",tinfo)

    comm.msend("done", "")

def GenDegreeDist(args):
    """
    generate degree distribution for all the nodes
        args, arguments as a string
    """

    largs = args.split()
    #print largs

    tname = largs[0]
    ns = int(largs[1])
    ne = int(largs[2])
    dis = largs[3]

    print "*task* %s %d %d %s" % (tname, ns, ne, dis)

    # TODO generate node degree distribution

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " <#nodes> <#ntasks>"
        sys.exit(1)

    nnodes = int(sys.argv[1])
    ntasks = int(sys.argv[2])

    comm.mclear()
    GenTasks(nnodes, ntasks, "std")
    comm.mexec(GenDegreeDist)

