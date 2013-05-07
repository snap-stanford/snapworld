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

    ds["dist"] += 1
    distance = ds["dist"]
    Visited = ds["visit"]
    #print "Visited", type(Visited)
    
    # nodes to add are on the input
    NewNodes = Snap.TIntH() 

    for item in msglist:

        name = sw.GetMsgName(item)

        #print "input", name
        # read the input nodes
        FIn = Snap.TFIn(Snap.TStr(name))
        Vec = Snap.TIntV(FIn)

        #print "len", Vec.Len()
        # get new nodes, not visited before
        Snap.GetNewNodes(Vec, Visited, NewNodes, distance);

    # done, no new nodes
    if NewNodes.Len() <= 0:
        # get distance distribution
        dcount = {}
        # TODO move this loop to SNAP C++
        VIter = Visited.BegI()
        while not VIter.IsEnd():
            snode = VIter.GetKey().Val
            distance = VIter.GetDat().Val
            if not dcount.has_key(distance):
                dcount[distance] = 0
            dcount[distance] += 1

            VIter.Next()

        # TODO move this loop to SNAP C++
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

        # TODO move this send to SNAP C++
        sw.Send(0,dmsgout,"2")

        sw.flog.write("final %s %s" % (str(ds["start"]), str(distance)))
        sw.flog.write("distances " + str(l) + "\n")
        sw.flog.flush()
        return

    # nodes in each task
    tsize = sw.GetRange()

    # collect nodes for the same task
    ntasks = int(sw.GetVar("gen_tasks"))
    Tasks = Snap.TIntIntVV(ntasks)

    # assign nodes to tasks
    Snap.Nodes2Tasks(NewNodes, Tasks, tsize)

    #for i in range(0,Tasks.Len()):
    #    print "sending task %d, len %d" % (i, Tasks.GetVal(i).Len())

    # send the messages
    for i in range(0,Tasks.Len()):
        Vec1 = Tasks.GetVal(i)
        if Vec1.Len() <= 0:
            continue

        # add task# at the end
        Vec1.Add(taskindex)
        sw.Send(i,Vec1,swsnap=True)

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

    #flog = sys.stdout
    fname = "log-swwork-%s.txt" % (sw.GetName())
    flog = open(fname,"a")

    sw.SetLog(flog)
    sw.GetConfig()

    Worker(sw)

    flog.write("finished\n")
    flog.flush()

