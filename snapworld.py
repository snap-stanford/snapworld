import random
import sys

import comm
import simplejson

#distmean = 150
#distvar  = 22.5
distmean = 5
distvar  = 1

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
        tinfo = "%d\t%d\t%s" % (ns, ne-1, dis)
        print tname, tinfo
        ns = ne
        comm.mroute("T0", tname, tinfo)

def StdDist(mean,dev):
    x = 0.0
    for i in range(0,12):
        x += random.random()

    x -= 6.0
    x *= dev
    x += mean

    return int(x + 0.5)

def GenStubs(tname,args):
    """
    determine degrees for all the nodes, generate the stubs and distribute them
        args, arguments as a string
    """

    argwords = args[0]
    largs = argwords.split("\t")
    #print largs

    ns = int(largs[0])
    ne = int(largs[1])
    dis = largs[2]

    print "*task* %s %d %d %s" % (tname, ns, ne, dis)

    # determine node degrees
    i = ns
    ddeg = {}
    while i <= ne:
        deg = StdDist(distmean,distvar)
        ddeg[i] = deg
        print "*task* %s, node %s, degree %s" % (tname, str(i), str(deg))
        i += 1

    print ddeg

    # distribute the stubs randomly to the tasks
    ntasks = comm.mgettasks()
    print "__tasks__ %s\t%s" % (tname, str(ntasks))
    
    # one item per task, each task has a list of stubs
    dstubs = {}
    for key,value in ddeg.iteritems():
        for i in range(0,value):
            t = int(random.random() * ntasks)
            if not dstubs.has_key(t):
                dstubs[t] = []
            dstubs[t].append(key)

    for key, value in dstubs.iteritems():
        tdst = "S%s" % (str(key))
        targs = simplejson.dumps(value)
        print tdst,targs
        comm.mroute(tname,tdst,targs)

def GenGraph(tname,args):

    # TODO, generate edges
    largs = []
    for item in args:
        l = simplejson.loads(item)
        largs.extend(l)
    print largs
    print tname,largs

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " <#nodes> <#tsize>"
        sys.exit(1)

    nnodes = int(sys.argv[1])
    tsize = int(sys.argv[2])

    ntasks = (nnodes+tsize-1)/tsize
    print "__tasks__\t%s" % (str(ntasks))

    comm.msettasks(ntasks)

    comm.mclear()

    # generate the tasks and assign nodes to them
    GenTasks(nnodes, tsize, "std")
    comm.msend("done", "")

    # generate node degrees and distribute stubs to tasks
    comm.mexec(GenStubs)
    comm.msend("done", "")

    # generate the random graph
    comm.mexec(GenGraph)
    comm.msend("done", "")

