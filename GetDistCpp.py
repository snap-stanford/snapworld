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
    Visited = Snap.TIntH(FIn)

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

    ds = LoadState()

    # process initialization
    if ds == None:

        # first iteration: input is the start node
        ds = InitState(taskindex, msglist)

    else:
        # successive iterations: input are the new nodes
        AddNewNodes(taskindex, sw, ds, msglist)

    SaveState(ds)

def InitState(taskindex, msglist):
    # TODO move all the message formats to SNAP
    # TODO move all the iterators to SNAP

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
    # TODO move all the message formats to SNAP
    # TODO move all the iterators to SNAP

    ds["dist"] += 1
    distance = ds["dist"]
    Visited = ds["visit"]
    print "Visited", type(Visited)
    
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
        VIter = Visited.BegI()
        while not VIter.IsEnd():
            snode = VIter.GetKey().Val
            distance = VIter.GetDat().Val
            if not dcount.has_key(distance):
                dcount[distance] = 0
            dcount[distance] += 1

            VIter.Next()

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

        sw.flog.write("final %s %s" % (str(ds["start"]), str(distance)))
        sw.flog.write("distances " + str(l) + "\n")
        sw.flog.flush()
        return

    # nodes in each task
    tsize = sw.GetRange()

    # collect nodes for the same task
    dtasks = {}
    NIter = NewNodes.BegI()
    while not NIter.IsEnd():
        ndst = NIter.GetKey().Val
        tn = TaskId(ndst,tsize)
        if not dtasks.has_key(tn):
            dtasks[tn] = []
        dtasks[tn].append(ndst)
        NIter.Next()

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

