import random
import sys

import comm
import simplejson

#distmean = 150
#distvar  = 22.5
distmean = 8
distvar  = 1

dispatch = {}

def TaskId(node,tsize):
    """
    return the task id for a node
    """

    return node/tsize

def GenTasks(tname,args):
    """
    generate the tasks
        args, arguments as a string

        nnodes, number of nodes
        tsize, number of nodes per task
        dis, degree distribution
    """

    step = int(tname.split("-")[1])

    d = simplejson.loads(args[0])
    nnodes = d["nnodes"]
    tsize = d["tsize"]
    dis = d["dis"]

    ns = 0
    tc = 0
    while ns < nnodes:
        tname = "G" + str(tc) + "-" + str(step+1)
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

    step = int(tname.split("-")[1])

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
        tdst = "S%s" % (str(key)) + "-" + str(step+1)
        targs = simplejson.dumps(value)
        print tdst,targs
        comm.mroute(tname,tdst,targs)

def GenGraph(tname,args):
    """
    generate the graph edges
        args, arguments as a string
    """

    step = int(tname.split("-")[1])

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
        tdst = TaskId(esrc, tsize)
        if not edges.has_key(tdst):
            edges[tdst] = []
        l = [esrc, edst]
        edges[tdst].append(l)

        tdst = TaskId(edst, tsize)
        if not edges.has_key(tdst):
            edges[tdst] = []
        l = [edst, esrc]
        edges[tdst].append(l)

    print tname,edges

    for key, value in edges.iteritems():
        tdst = "E%s" % (str(key)) + "-" + str(step+1)
        targs = simplejson.dumps(value)
        print tdst,targs
        comm.mroute(tname,tdst,targs)

def GenNbr(tname,args):
    """
    generate the graph neighbors
        args, arguments as a string
    """

    task = tname.split("-")[0]
    step = int(tname.split("-")[1])

    # extract neighbors from the args
    # iterate through the input queue and add new items to the neighbor list
    edges = []
    for item in args:
        l = simplejson.loads(item)
        edges.extend(l)
    print edges
    print tname,edges

    # collect neighbors for each node
    nbrs = {}
    for item in edges:
        src = item[0]
        dst = item[1]
        if not nbrs.has_key(src):
            nbrs[src] = set()
        nbrs[src].add(dst)

    for node, edges in nbrs.iteritems():
        print tname, node, edges

    # select a random node for stats
    nsel = random.choice(list(nbrs.keys()))
    print tname, "sel", nsel

    # send the node and its neighbors to the distance task
    step += 1
    tdst = "D%s" % (str(nsel)) + "-" + str(step)
    dmsg = {}
    dmsg["node"] = nsel
    dmsg["nbrs"] = list(nbrs[nsel])
    targs = simplejson.dumps(dmsg)
    print tdst,targs
    comm.mroute(tname,tdst,targs)

    while True:
        yield

        step += 1
        tname = task + "-" + str(step)
        args = comm.mgetargs(tname)

        # iterate through the input queue, get the nodes, report neighbors
        step += 1
        for item in args:
            d = simplejson.loads(item)
            tdst = d["task"] + "-" + str(step)
            nodes = d["nodes"]
            for node in nodes:
                dmsg = {}
                dmsg["node"] = node
                dmsg["nbrs"] = list(nbrs[node])
                targs = simplejson.dumps(dmsg)
                tdst = "D%s" % (str(node)) + "-" + str(step)
                print tdst,targs
                comm.mroute(tname,tdst,targs)

def GetDist(tname,args):
    """
    find the node distance
        args, arguments as a string
    """

    print "GetDist", tname

    task = tname.split("-")[0]
    step = int(tname.split("-")[1])
    tsize = comm.mgetconfig("tsize")

    # get the initial arguments: starting node and its neighbors
    dinit = simplejson.loads(args[0])
    node = dinit["node"]
    nbrlist = dinit["nbrs"]

    # no visited nodes yet, first iteration
    visited = {}
    distance = 0

    while True:

        # process the new neighbors
        distance += 1
        newnodes = []

        # process all the input elements
        for arg in args:
            dinit = simplejson.loads(arg)
            srcnode = dinit["node"]
            nbrlist = dinit["nbrs"]

            for item in nbrlist:
                # skip nodes already visited
                if item in visited:
                    continue
    
                # add new nodes to the visited nodes and the new nodes
                visited[item] = distance
                newnodes.append(item)
    
        # done, if there are no more new nodes
        if len(newnodes) <= 0:
            break

        # send new visited nodes to the graph nodes to find their neighbors
    
        # collect nodes for the same task
        dtasks = {}
        for ndst in newnodes:
            tn = TaskId(ndst,tsize)
            if not dtasks.has_key(tn):
                dtasks[tn] = []
            dtasks[tn].append(ndst)
    
        # send the messages
        step += 1
        for tn,args in dtasks.iteritems():
            dmsg = {}
            dmsg["task"] = task
            dmsg["nodes"] = args
            tdst = "E%s" % (str(tn)) + "-" + str(step)
            targs = simplejson.dumps(dmsg)
            print tdst,targs
            comm.mroute(tname,tdst,targs)

        # wait for another iteration
        yield

        # move the task name to the next step
        step += 1
        tname = task + "-" + str(step)

        # get the input queue
        args = comm.mgetargs(tname)

        # end of while, repeat the loop

    # TODO calculate statistics
    print "*finish*", tname
    return

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

    # define the function dispatch table

    d = {}
    d["type"] = "func"
    d["def" ] = GenTasks
    dispatch["T"] = d

    d = {}
    d["type"] = "func"
    d["def" ] = GenStubs
    dispatch["G"] = d

    d = {}
    d["type"] = "func"
    d["def" ] = GenGraph
    dispatch["S"] = d

    d = {}
    d["type"] = "iter"
    d["def" ] = GenNbr
    dispatch["E"] = d

    d = {}
    d["type"] = "iter"
    d["def" ] = GetDist
    dispatch["D"] = d

    comm.msetdispatch(dispatch)

    d = {}
    d["nnodes"] = nnodes
    d["tsize"] = tsize
    d["dis"] = "std"
    targs = simplejson.dumps(d)

    comm.mroute("00","T0-0",targs)

    # generate the tasks and assign nodes to them
    #GenTasks(nnodes, tsize, "std")
    comm.mexec()

    # generate node degrees and distribute stubs to tasks
    #comm.mexec(GenStubs)
    comm.mexec()

    # generate the random graph
    #comm.mexec(GenGraph)
    comm.mexec()

    # generate the graph statistics
    #comm.mexec(GenNbr)
    comm.mexec()

    # calculate node distance
    #comm.mexec(GetDist)
    comm.mexec()

    #comm.mexec(GenNbr)
    comm.mexec()

    # continue processing while there are some messages
    #while comm.mcontinue():
    #    comm.mexec()

