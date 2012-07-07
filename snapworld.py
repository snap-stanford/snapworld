import random
import sys

import comm
import simplejson

#distmean = 150
#distvar  = 22.5
distmean = 8
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
        tname = "G" + str(tc)
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
    ntasks = comm.mgetconfig("tasks")
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
    """
    generate the graph edges
        args, arguments as a string
    """

    # extract the stubs from the args
    # iterate through the input queue and add new items to the stub list
    stubs = []
    for item in args:
        l = simplejson.loads(item)
        stubs.extend(l)
    #print stubs
    print tname,stubs

    # randomize the items
    random.shuffle(stubs)
    #print tname + "-r",stubs

    # get the pairs
    pairs = zip(stubs[::2], stubs[1::2])

    print tname,pairs
    
    # distribute the stubs randomly to the tasks
    tsize = comm.mgetconfig("tsize")

    # get edges for a specific task
    edges = {}
    for pair in pairs:
        esrc = pair[0]
        edst = pair[1]

        # add the edge twice for both directions
        tdst = esrc / tsize
        if not edges.has_key(tdst):
            edges[tdst] = []
        l = [esrc, edst]
        edges[tdst].append(l)

        tdst = edst / tsize
        if not edges.has_key(tdst):
            edges[tdst] = []
        l = [edst, esrc]
        edges[tdst].append(l)

    print tname,edges

    for key, value in edges.iteritems():
        tdst = "E%s" % (str(key))
        targs = simplejson.dumps(value)
        print tdst,targs
        comm.mroute(tname,tdst,targs)

def GenStat(tname,args):
    """
    generate the graph statistics
        args, arguments as a string
    """

    # extract edges from the args
    # iterate through the input queue and add new items to the edge list
    edges = []
    for item in args:
        l = simplejson.loads(item)
        edges.extend(l)
    print edges
    print tname,edges

    # collect edges for each node
    nodes = {}
    for item in edges:
        src = item[0]
        dst = item[1]
        if not nodes.has_key(src):
            nodes[src] = []
        nodes[src].append(dst)

    for node, edges in nodes.iteritems():
        print tname, node, edges

    # TODO implement the graph stats

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " <#nodes> <#tsize>"
        sys.exit(1)

    nnodes = int(sys.argv[1])
    tsize = int(sys.argv[2])

    ntasks = (nnodes+tsize-1)/tsize
    print "__tasks__\t%s" % (str(ntasks))

    comm.msetconfig("nnodes",nnodes)
    comm.msetconfig("tsize",tsize)
    comm.msetconfig("tasks",ntasks)

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

    # generate the graph statistics
    comm.mexec(GenStat)
    comm.msend("done", "")

