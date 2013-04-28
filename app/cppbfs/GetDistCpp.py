import os
import random
import sys

import snap as Snap
import swlib

def GetDist(sw):
    """
    find the node distance
    """

    taskname = sw.GetName()
    taskindex = int(taskname.split("-")[1])

    msglist = sw.GetMsgList()
    sw.log.debug("msglist %s" % str(msglist))

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
    Visited.AddDat(node,0)

    ds["visit"] = Visited

    tsize = sw.GetRange()
    tn = TaskId(node,tsize)

    # send the message
    Vec1 = Snap.TIntV()
    Vec1.Add(node)
    Vec1.Add(taskindex)
    sw.Send(tn,Vec1,swsnap=True)

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

        name = sw.GetMsgName(item)

        print "input", name
        # read the input nodes
        FIn = Snap.TFIn(Snap.TStr(name))
        Vec = Snap.TIntV(FIn)

        # TODO iterate through nodes
        print "len", Vec.Len()
        for i in range(0,Vec.Len()):
            Node = Vec.GetVal(i).Val
            print "Vec", i, Node

            if Visited.IsKey(Node):
                continue
            NewNodes.AddDat(Node,0)
            Visited.AddDat(Node,distance)

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

        sw.log.info("final %s %s" % (str(ds["start"]), str(distance)))
        sw.log.info("distances %s" % str(l))
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

        # output is composed of: nodes, task#
        Vec1 = Snap.TIntV()
        for node in args:
            Vec1.Add(node)

        Vec1.Add(taskindex)

        sw.Send(tn,Vec1,swsnap=True)

def TaskId(node,tsize):
    """
    return the task id for a node
    """

    return node/tsize

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

def Worker(sw):
    GetDist(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    fname = "log-swwork-%s.txt" % (sw.GetName())

    sw.SetLog(fname)
    sw.GetConfig()

    Worker(sw)

    sw.log.info("finished")

