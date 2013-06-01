import os
import random
import sys
import time

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

    #t2 = time.time()
    #tmsec = int(t2*1000) % 1000
    #print "%s.%03d loadstate start" % (time.ctime(t2)[11:19], tmsec)
    ds = LoadState()
    #t2 = time.time()
    #tmsec = int(t2*1000) % 1000
    #print "%s.%03d loadstate end" % (time.ctime(t2)[11:19], tmsec)

    # process initialization
    if ds == None:

        # first iteration: input is the start node
        ds = InitState(taskindex, msglist)

    else:
        # successive iterations: input are the new nodes
        AddNewNodes(taskindex, sw, ds, msglist)

    #t2 = time.time()
    #tmsec = int(t2*1000) % 1000
    #print "%s.%03d savestate start" % (time.ctime(t2)[11:19], tmsec)
    SaveState(ds)
    #t2 = time.time()
    #tmsec = int(t2*1000) % 1000
    #print "%s.%03d savestate end" % (time.ctime(t2)[11:19], tmsec)

def InitState(taskindex, msglist):

    # the original node is on input
    node = None
    for item in msglist:
        msg = sw.GetMsg(item)
        d = msg["body"]

    ns = d["s"]
    nrange = d["r"]
    node = d.get("source",-1)

    ds = {}
    ds["first"] = ns
    ds["range"] = nrange
    ds["count"] = 0
    ds["dist"] = 0
    ds["start"] = node

    Visited = Snap.TIntV(nrange) 
    Snap.ZeroVec(Visited)
    if node >= 0:
        Visited.GetVal(node-ns).Val = 1  # set start node to 1, reset to 0 at the end
        ds["count"] = 1

    ds["visit"] = Visited

    tsize = sw.GetRange()
    tn = TaskId(node,tsize)

    # send the message
    if node >= 0:
        Vec1 = Snap.TIntV()
        Vec1.Add(node)
        Vec1.Add(0)
        sw.Send(tn,Vec1,swsnap=True)

    return ds

def AddNewNodes(taskindex, sw, ds, msglist):

    # all the nodes were visited already
    if ds["count"] >= ds["range"]:
        return

    distance = -1
    Visited = ds["visit"]
    #print "Visited", type(Visited)
    
    # nodes to add are on the input
    NewNodes = Snap.TIntV() 

    t1 = time.time()
    for item in msglist:

        name = sw.GetMsgName(item)

        #t2 = time.time()
        #tmsec = int(t2*1000) % 1000
        #tdiff = (t2 - t1)
        #print "%s.%03d %.3f input   %s" % (
        #        time.ctime(t2)[11:19], tmsec, tdiff, name)
        #t1 = t2

        # read the input nodes
        FIn = Snap.TFIn(Snap.TStr(name))
        Vec = Snap.TIntV(FIn)
        distance = Vec.Last().Val + 1
        Vec.DelLast()

        # subtract the starting index
        Snap.IncVal(Vec, -ds["first"])

        #t2 = time.time()
        #tmsec = int(t2*1000) % 1000
        #tdiff = (t2 - t1)
        #print "%s.%03d %.3f reading %s" % (
        #        time.ctime(t2)[11:19], tmsec, tdiff, name)
        #t1 = t2

        #print "len", Vec.Len()
        # get new nodes, not visited before
        Snap.GetNewNodes1(Vec, Visited, NewNodes, distance);

        #t2 = time.time()
        #tmsec = int(t2*1000) % 1000
        #tdiff = (t2 - t1)
        #print "%s.%03d %.3f compute %s" % (
        #        time.ctime(t2)[11:19], tmsec, tdiff, name)
        #t1 = t2

    ds["dist"] = distance
    
    nnodes = ds["range"]
    ds["count"] += NewNodes.Len()

    sw.flog.write("distance %d, new %d, count %d, nodes %d\n" % (
                    distance, NewNodes.Len(), ds["count"], nnodes))
    sw.flog.flush()

    # done, no new nodes
    #if NewNodes.Len() <= 0:
    sw.flog.write("testing %d %d %d\n" % (ds["count"], nnodes, ds["count"] >= nnodes))
    sw.flog.flush()
    if ds["count"] >= nnodes:
        #t2 = time.time()
        #tmsec = int(t2*1000) % 1000
        #print "%s.%03d output start" % (time.ctime(t2)[11:19], tmsec)
        #t1 = t2

        sw.flog.write("sending finish output\n")
        sw.flog.flush()

        if ds["start"] >= 0:
            # reset start node to 0
            Visited.GetVal(ds["start"]-ds["first"]).Val = 0

        # get distance distribution, assume 1000 is the max
        DistCount = Snap.TIntV(1000)
        Snap.ZeroVec(DistCount)
        Snap.GetDistances(Visited,DistCount)

        #for i in xrange(0, DistCount.Len()):
        #    print "dist", i, DistCount.GetVal(i).Val

        #for snode in xrange(0,nnodes):
        #    distance = Visited.GetVal(snode).Val

        #    if not dcount.has_key(distance):
        #        dcount[distance] = 0
        #    dcount[distance] += 1

        # get the maximum positive distance
        maxdist = DistCount.Len()-1
        while (maxdist > 0)  and  (DistCount.GetVal(maxdist).Val == 0):
            maxdist -= 1

        maxdist += 1

        sw.flog.write("maxdist %d\n" % (maxdist))
        sw.flog.flush()

        # collect the distances
        l = []
        for i in xrange(0, maxdist):
            #if DistCount.GetVal(i).Val <= 0:
            #    break
            l.append(DistCount.GetVal(i).Val)

        dmsg = {}
        dmsg["start"] = ds["start"]
        dmsg["dist"] = l

        dmsgout = {}
        dmsgout["src"] = sw.GetName()
        dmsgout["cmd"] = "results"
        dmsgout["body"] = dmsg

        sw.Send(0,dmsgout,"2")

        sw.flog.write("final %s %s\n" % (str(ds["start"]), str(distance)))
        sw.flog.write("distances " + str(l) + "\n")
        sw.flog.flush()
        #t2 = time.time()
        #tmsec = int(t2*1000) % 1000
        #tdiff = (t2 - t1)
        #print "%s.%03d %.3f output done" % (
        #        time.ctime(t2)[11:19], tmsec, tdiff)

    # nodes in each task
    tsize = sw.GetRange()

    # collect nodes for the same task
    ntasks = int(sw.GetVar("gen_tasks"))
    Tasks = Snap.TIntIntVV(ntasks)

    Snap.IncVal(NewNodes, ds["first"])

    # assign nodes to tasks
    Snap.Nodes2Tasks1(NewNodes, Tasks, tsize)

    #for i in range(0,Tasks.Len()):
    #    print "sending task %d, len %d" % (i, Tasks.GetVal(i).Len())

    # send the messages
    for i in range(0,Tasks.Len()):
        Vec1 = Tasks.GetVal(i)
        if Vec1.Len() <= 0:
            continue

        # add task# at the end
        Vec1.Add(distance)
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
    First = Snap.TInt(FIn)
    Range = Snap.TInt(FIn)
    Count = Snap.TInt(FIn)
    Dist = Snap.TInt(FIn)
    Start = Snap.TInt(FIn)
    Visited = Snap.TIntV(FIn)

    ds = {}
    ds["first"] = First.Val
    ds["range"] = Range.Val
    ds["count"] = Count.Val
    ds["dist"] = Dist.Val
    ds["start"] = Start.Val
    ds["visit"] = Visited
    return ds

def SaveState(ds):
    fname = sw.GetStateName()

    First = Snap.TInt(ds["first"])
    Range = Snap.TInt(ds["range"])
    Count = Snap.TInt(ds["count"])
    Dist = Snap.TInt(ds["dist"])
    Start = Snap.TInt(ds["start"])
    Visited = ds["visit"]

    FOut = Snap.TFOut(Snap.TStr(fname))
    First.Save(FOut)
    Range.Save(FOut)
    Count.Save(FOut)
    Dist.Save(FOut)
    Start.Save(FOut)
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

