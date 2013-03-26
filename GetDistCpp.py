import os
import random
import sys

import snap as Snap
import swlib

def LoadState():
    fname = sw.GetStateName()
    if not os.path.exists(fname):
        return None

    FIn = Snap.TFIn(Snap.TStr(fname))
    Start = Snap.TInt(FIn)
    Dist = Snap.TInt(FIn)
    Visited = Snap.TIntV(FIn)

    ds = {}
    ds["start"] = Start.Val
    ds["dist"] = Dist.Val
    ds["visit"] = Visited
    return ds

def SaveState(ds):
    fname = sw.GetStateName()

    Start = Snap.TInt(ds["start"])
    Dist = Snap.TInt(ds["dist"])
    Visited = ds["visit"]

    FOut = Snap.TFOut(Snap.TStr(fname))
    Start.Save(FOut)
    Dist.Save(FOut)
    Visited.Save(FOut)
    FOut.Flush()

def TaskId(node,tsize):
    """
    return the task id for a node
    """

    return node/tsize

def GetDist(sw):
    """
    find the node distance
    """

    taskname = sw.GetName()
    taskindex = taskname.split("-")[1]

    msglist = sw.GetMsgList()
    sw.flog.write("msglist " + str(msglist) + "\n")
    sw.flog.flush()

    print 11
    ds = LoadState()
    print 12

    # process initialization
    if ds == None:

        # first iteration: input is the start node
        ds = InitState(taskindex, msglist)

    else:
        # successive iterations: input are the new nodes
        AddNewNodes(taskindex, sw, ds, msglist)

    SaveState(ds)

def InitState(taskindex, msglist):

    # the original node is on input
    node = None
    for item in msglist:
        msg = sw.GetMsg(item)
        node = msg["body"]

    ds = {}
    ds["start"] = node
    ds["dist"] = 0

    Visited = Snap.TIntH() 
    print 1
    Visited.AddDat(node,0)
    print 2

    ds["visit"] = Visited

    tsize = sw.GetRange()
    tn = TaskId(node,tsize)

    dmsg = {}
    dmsg["task"] = taskindex
    dmsg["nodes"] = [node]

    dmsgout = {}
    dmsgout["src"] = sw.GetName()
    dmsgout["cmd"] = "nbrs"
    dmsgout["body"] = dmsg

    sw.Send(tn,dmsgout)

    return ds

def AddNewNodes(taskindex, sw, ds, msglist):

    ds["dist"] += 1
    distance = ds["dist"]
    Visited = ds["visit"]
    
    # nodes to add are on the input
    NewNodes = Snap.TIntH() 
    for item in msglist:
        msg = sw.GetMsg(item)
        nodes = msg["body"]
        for node in nodes:
            if Visited.IsKey(node):
                continue
            NewNodes.AddDat(node,0)
            Visited.AddDat(node,distance)

    # done, no new nodes
    if NewNodes.Len() <= 0:
        # get distance distribution
        dcount = {}
        for snode,distance in visited.iteritems():
            if not dcount.has_key(distance):
                dcount[distance] = 0
            dcount[distance] += 1

        nnodes = int(sw.GetVar("nodes"))
        l = []
        for i in range(0, nnodes):
            if not dcount.has_key(i):
                break
            l.append(dcount[i])

        dmsg = {}
        dmsg["start"] = ds["start"]
        dmsg["dist"] = l

        dmsgout = {}
        dmsgout["src"] = sw.GetName()
        dmsgout["cmd"] = "results"
        dmsgout["body"] = dmsg

        sw.Send(0,dmsgout,"2")

        sw.flog.write("final " + ds["start"] + " " + str(distance) + " " + str(visited) + "\n")
        sw.flog.write("distances " + str(l) + "\n")
        sw.flog.flush()
        return

    # nodes in each task
    tsize = sw.GetRange()

    # collect nodes for the same task
    dtasks = {}
    for ndst in newnodes:
        tn = TaskId(ndst,tsize)
        if not dtasks.has_key(tn):
            dtasks[tn] = []
        dtasks[tn].append(ndst)

    #print "dtasks", dtasks

    # send the messages
    for tn,args in dtasks.iteritems():
        dmsg = {}
        dmsg["task"] = taskindex
        dmsg["nodes"] = args

        dmsgout = {}
        dmsgout["src"] = sw.GetName()
        dmsgout["cmd"] = "nbrs"
        dmsgout["body"] = dmsg

        sw.Send(tn,dmsgout)

def Worker(sw):
    GetDist(sw)

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

