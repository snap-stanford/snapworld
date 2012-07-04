import random
import sys

import comm

def GenTasks(nnodes, tsize, dis):
    """
    generate the tasks
        nnodes, number of nodes
        tsize, number of nodes per task
        dis, degree distribution
    """

    ns = 0
    tc = 0
    while ns < nnodes:
        tname = str(tc)
        tc += 1
        ne = ns + tsize
        if ne > nnodes:
            ne = nnodes
        tinfo = "%s %d %d %s" % (tname, ns, ne-1, dis)
        print tinfo
        ns = ne
        comm.msend("task",tinfo)

    comm.msend("done", "")

def StdDist(mean,dev):
    x = 0.0
    for i in range(0,12):
        x += random.random()

    x -= 6.0
    x *= dev
    x += mean

    return int(x + 0.5)

def GenStubs(args):
    """
    determine degrees for all the nodes, generate the stubs and distribute them
        args, arguments as a string
    """

    largs = args.split()
    #print largs

    tname = largs[0]
    ns = int(largs[1])
    ne = int(largs[2])
    dis = largs[3]

    print "*task* %s %d %d %s" % (tname, ns, ne, dis)

    # determine node degrees
    i = ns
    while i <= ne:
        deg = StdDist(150,22.5)
        print "*task* %s, node %s, degree %s" % (tname, str(i), str(deg))
        i += 1

    # TODO distribute the stubs

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " <#nodes> <#tsize>"
        sys.exit(1)

    nnodes = int(sys.argv[1])
    tsize = int(sys.argv[2])

    comm.mclear()

    # generate the tasks and assign nodes to them
    GenTasks(nnodes, tsize, "std")

    # generate node degrees and distribute stubs to tasks
    comm.mexec(GenStubs)

