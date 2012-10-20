import random
import os
import simplejson
import sys

import swlib

def GenNbr(sw):
    """
    generate the graph neighbors
    """

    taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.flog.write("msglist " + str(msglist) + "\n")
    sw.flog.flush()

    ds = sw.LoadState()

    # process initialization
    if ds == None:
        ds = GetEdges(sw)
        sw.SaveState(ds)
        SelectNode(sw, ds)

    else:
        GetNeighbors(sw, ds)


def GetEdges(sw):
    # extract neighbors from the args
    # iterate through the input queue and add new items to the neighbor list
    edges = []
    for item in msglist:
        msg = sw.GetMsg(item)
        edges.extend(l)

    #print edges
    #print taskname,edges

    # collect neighbors for each node
    nbrs = {}
    for item in edges:
        src = item[0]
        dst = item[1]
        if not nbrs.has_key(src):
            nbrs[src] = set()
        nbrs[src].add(dst)

    return nbrs

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
--- this part is missing

def SelectNode(sw, ds):

    #for node, edges in nbrs.iteritems():
    #    print taskname, node, edges

    # select a random node for stats
    nsel = random.choice(list(nbrs.keys()))
    #nsel = list(nbrs.keys())[0]
    sw.flog.write("task %s, sel %d\n" % (taskname, nsel))
    sw.flog.flush()

    # send the node and its neighbors to the distance task
    tdst = "D%s" % (str(nsel))
    dmsg = {}
    dmsg["node"] = nsel
    dmsg["nbrs"] = list(nbrs[nsel])
    targs = simplejson.dumps(dmsg)
    print tdst,targs
    comm.mroute(tname,tdst,targs)

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
--- this part is missing

def GetNeighbors(sw, ds):

    while True:
        yield

        args = comm.mgetargs(tname)
        if args == None:
            continue

        # iterate through the input queue, get the nodes, report neighbors
        for item in args:
            d = simplejson.loads(item)
            tdst = d["task"]
            nodes = d["nodes"]
            for node in nodes:
                dmsg = {}
                dmsg["node"] = node
                dmsg["nbrs"] = list(nbrs[node])
                targs = simplejson.dumps(dmsg)
                #tdst = "D%s" % (str(node))
                print tdst,targs
                comm.mroute(tname,tdst,targs)
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def Worker(sw):
    GenNbr(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    #flog = sys.stdout
    fname = "log-swwork-%s.txt" % (sw.GetName())
    flog = open(fname,"w")

    sw.SetLog(flog)
    sw.GetConfig()

    Worker(sw)

    flog.write("finished\n")
    flog.flush()

