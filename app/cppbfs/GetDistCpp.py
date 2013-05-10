import os
import random
import sys
import traceback

import snap as Snap
import swlib

import perf

def GetDist(sw):
    """
    find the node distance
    """

    taskname = sw.GetName()
    taskindex = int(taskname.split("-")[1])

    msglist = sw.GetMsgList()
    sw.log.debug("msglist: %s" % msglist)

    with perf.Timer(sw.log, "LoadState-GetDistCpp"):
        ds = LoadState(sw)

    # process initialization
    if ds == None:

        # first iteration: input is the start node
        with perf.Timer(sw.log, "InitState-GetDistCpp"):
            ds = InitState(sw, taskindex, msglist)

    else:
        # successive iterations: input are the new nodes
        with perf.Timer(sw.log, "AddNewNodes-GetDistCpp"):
            AddNewNodes(taskindex, sw, ds, msglist)

    with perf.Timer(sw.log, "SaveState-GetDistCpp"):
        SaveState(sw, ds)

def InitState(sw, taskindex, msglist):

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
    # print "Visited", type(Visited)

    timer = perf.Timer(sw.log)
    
    # nodes to add are on the input
    NewNodes = Snap.TIntH() 

    timer.start("dist-msglist-iter")

    perf.DirSize(sw.log, sw.qin, "GetDist-qin")

    for item in msglist:

        name = sw.GetMsgName(item)

        # print "input", name
        # read the input nodes
        FIn = Snap.TFIn(Snap.TStr(name))
        Vec = Snap.TIntV(FIn)

        # print "len", Vec.Len()
        # get new nodes, not visited before
        timer.start("dist-nodes-iter")
        Snap.GetNewNodes(Vec, Visited, NewNodes, distance)
        timer.stop("dist-nodes-iter")

    timer.stop("dist-msglist-iter")

    # done, no new nodes
    if NewNodes.Len() <= 0:
        timer.start("dist-get-distribution")
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

        nnodes = int(sw.GetVar("nodes"))
        l = []
        for i in xrange(0, nnodes):
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

        timer.stop("dist-get-distribution")
        return

    # nodes in each task
    tsize = sw.GetRange()

    timer.start("dist-collect-nodes")

    # collect nodes for the same task
    ntasks = int(sw.GetVar("gen_tasks"))
    Tasks = Snap.TIntIntVV(ntasks)

    # assign nodes to tasks
    Snap.Nodes2Tasks(NewNodes, Tasks, tsize)

    timer.stop("dist-collect-nodes")

    # for i in range(0,Tasks.Len()):
    #     print "sending task %d, len %d" % (i, Tasks.GetVal(i).Len())

    # send the messages
    timer.start("dist-send-all")
    for i in range(0,Tasks.Len()):
        Vec1 = Tasks.GetVal(i)
        if Vec1.Len() <= 0:
            continue

        # add task# at the end
        Vec1.Add(taskindex)
        sw.Send(i,Vec1,swsnap=True)
    timer.stop("dist-send-all")

def TaskId(node,tsize):
    """
    return the task id for a node
    """

    return node/tsize

def LoadState(sw):
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

def SaveState(sw, ds):
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

def main():
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    fname = "swwork-%s.log" % (sw.GetName())

    sw.SetLog(fname)
    sw.GetConfig()

    Worker(sw)

    sw.log.info("finished")

if __name__ == '__main__':
    try:
        main()
    except:
        sys.stdout.write("[ERROR] Exception in GenDistCpp.main()\n")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(2)

