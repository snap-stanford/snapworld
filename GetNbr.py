import os
import random
import sys

import swlib

def GetNbr(sw):
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

        # first iteration: input are edges, save the state
        ds = GetEdges(msglist)
        sw.flog.write("state " + str(ds) + "\n")
        sw.flog.flush()
        sw.SaveState(ds)

    else:
        # successive iterations: input are nodes, report the edges
        GetNeighbors(sw, ds, msglist)


def GetEdges(msglist):
    # extract neighbors from the args
    # iterate through the input queue and add new items to the neighbor list
    edges = []
    for item in msglist:
        msg = sw.GetMsg(item)
        edges.extend(msg)

    #print edges
    sw.flog.write("edges " + str(edges) + "\n")
    sw.flog.flush()

    # collect neighbors for each node
    nbrs = {}
    for item in edges:
        src = item[0]
        dst = item[1]
        if not nbrs.has_key(src):
            nbrs[src] = set()
        nbrs[src].add(dst)

    # convert sets to lists
    d = {}
    for key, value in nbrs.iteritems():
        d[key] = list(value)

    return d

def GetNeighbors(sw, ds, msglist):
    # iterate through the input queue, get the nodes, report neighbors

    edges = []
    for item in msglist:
        d = sw.GetMsg(item)
        tdst = d["task"]
        nodes = d["nodes"]
        s = set()
        for node in nodes:
            snode = str(node)
            s = s.union(set(ds[snode]))

        dmsg = list(s)
        sw.Send(tdst,dmsg)

def Worker(sw):
    GetNbr(sw)

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

