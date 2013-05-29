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
        node = msg["body"]

    ds = {}
    ds["start"] = node
    ds["dist"] = 0
    #ds["count"] = 1

    nnodes = int(sw.GetVar("nodes"))
    Visited = Snap.TIntV(nnodes) 
    Snap.ZeroVec(Visited)
    Visited.GetVal(node).Val = 1  # set start node to 1, reset to 0 at the end

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

    nnodes = int(sw.GetVar("nodes"))
    #ds["count"] += NewNodes.Len()

    # done, no new nodes
    #if ds["count"] >= nnodes:
    if NewNodes.Len() <= 0:
        #t2 = time.time()
        #tmsec = int(t2*1000) % 1000
        #print "%s.%03d output start" % (time.ctime(t2)[11:19], tmsec)
        #t1 = t2

        Visited.GetVal(ds["start"]).Val = 0    # reset start node to 0

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

        l = []
        for i in xrange(0, DistCount.Len()):
            if DistCount.GetVal(i).Val <= 0:
                break
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
        return

    # nodes in each task
    tsize = sw.GetRange()

    # collect nodes for the same task
    ntasks = int(sw.GetVar("gen_tasks"))
    Tasks = Snap.TIntIntVV(ntasks)

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
    #Count = Snap.TInt(FIn)
    Visited = Snap.TIntV(FIn)

    ds = {}
    ds["start"] = Start.Val
    ds["dist"] = Dist.Val
    #ds["count"] = Count.Val
    ds["visit"] = Visited
    return ds

def SaveState(ds):
    fname = sw.GetStateName()

    Start = Snap.TInt(ds["start"])
    Dist = Snap.TInt(ds["dist"])
    #Count = Snap.TInt(ds["count"])
    Visited = ds["visit"]

    FOut = Snap.TFOut(Snap.TStr(fname))
    Start.Save(FOut)
    Dist.Save(FOut)
    #Count.Save(FOut)
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

