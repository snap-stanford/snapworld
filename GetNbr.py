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
    
    edges = []
    for item in msglist:
        dmsg = sw.GetMsg(item)
        cmd = dmsg["cmd"]
        msg = dmsg["body"]

        if cmd == "init":
            edges.extend(msg)
        else:
            GetNeighbors(sw, ds, msg)

    if len(edges) > 0:
        # first iteration: input are edges, save the state
        ds = GetEdges(edges)
        sw.flog.write("state " + str(ds) + "\n")
        sw.flog.flush()
        sw.SaveState(ds)

        dmsgout = {}
        dmsgout["src"] = sw.GetName()
        dmsgout["cmd"] = "targets"
        dmsgout["body"] = {}
        sw.Send(0,dmsgout,"2")

def GetEdges(edges):

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

def GetNeighbors(sw, ds, msg):
    # report node neighbors

    tdst = msg["task"]
    nodes = msg["nodes"]
    s = set()
    for node in nodes:
        snode = str(node)
        s = s.union(set(ds[snode]))

    dmsgout = {}
    dmsgout["src"] = sw.GetName()
    dmsgout["cmd"] = "nbrs"
    dmsgout["body"] = list(s)
    sw.Send(tdst,dmsgout)

def Worker(sw):
    GetNbr(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    #flog = sys.stdout
    fname = "log-swwork-%s.txt" % (sw.GetName())
    flog = open(fname,"a")

    sw.SetLog(flog)
    sw.GetConfig()

    Worker(sw)

    flog.write("finished\n")
    flog.flush()

