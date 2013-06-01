import os
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

    sw.cum_timer.cum_start("disk")

    msglist = sw.GetMsgList()
    sw.log.debug("msglist: %s" % msglist)

    with perf.Timer(sw.log, "LoadState-GetDistCpp"):
        ds = LoadState(sw)

    sw.cum_timer.cum_stop("disk")

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
    sw.cum_timer.cum_start("disk")
    for item in msglist:
        msg = sw.GetMsg(item)
        d = msg["body"]
    sw.cum_timer.cum_stop("disk")

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
        # set start node to 1, reset to 0 at the end
        Visited.GetVal(node-ns).Val = 1
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

    timer = perf.Timer(sw.log)
    
    # nodes to add are on the input
    NewNodes = Snap.TIntV()

    timer.start("dist-msglist-iter")

    perf.DirSize(sw.log, sw.qin, "GetDist-qin")

    for item in msglist:

        sw.cum_timer.cum_start("disk")

        name = sw.GetMsgName(item)

        # read the input nodes
        FIn = Snap.TFIn(Snap.TStr(name))
        Vec = Snap.TIntV(FIn)

        sw.cum_timer.cum_stop("disk")

        distance = Vec.Last().Val + 1
        Vec.DelLast()

        # subtract the starting index
        Snap.IncVal(Vec, -ds["first"])

        #print "len", Vec.Len()
        # get new nodes, not visited before
        timer.start("dist-nodes-iter")
        Snap.GetNewNodes1(Vec, Visited, NewNodes, distance);
        timer.stop("dist-nodes-iter")

    timer.stop("dist-msglist-iter")

    ds["dist"] = distance
    
    nnodes = ds["range"]
    ds["count"] += NewNodes.Len()


    sw.log.info("distance: %d, new: %d, count: %d, nodes: %d" % \
            (distance, NewNodes.Len(), ds["count"], nnodes))

    # done, no new nodes
    sw.log.debug("testing: %d %d %d" % \
            (ds["count"], nnodes, ds["count"] >= nnodes))

    if ds["count"] >= nnodes:

        sw.log.info("sending finish output")

        if ds["start"] >= 0:
            # reset start node to 0
            Visited.GetVal(ds["start"]-ds["first"]).Val = 0

        # get distance distribution, assume 1000 is the max
        DistCount = Snap.TIntV(1000)
        Snap.ZeroVec(DistCount)
        Snap.GetDistances(Visited,DistCount)

        # get the maximum positive distance
        maxdist = DistCount.Len()-1
        while (maxdist > 0) and (DistCount.GetVal(maxdist).Val == 0):
            maxdist -= 1

        maxdist += 1

        sw.log.info("maxdist: %d" % maxdist)

        # collect the distances
        l = []
        for i in xrange(maxdist):
            # if DistCount.GetVal(i).Val <= 0: break
            l.append(DistCount.GetVal(i).Val)

        dmsg = {}
        dmsg["start"] = ds["start"]
        dmsg["dist"] = l

        dmsgout = {}
        dmsgout["src"] = sw.GetName()
        dmsgout["cmd"] = "results"
        dmsgout["body"] = dmsg

        sw.cum_timer.cum_start("network")
        sw.Send(0,dmsgout,"2")
        sw.cum_timer.cum_stop("network")

        sw.log.info("final: %s %s" % (str(ds["start"]), str(distance)))
        sw.log.info("distances: %s" % str(l))

    # nodes in each task
    tsize = sw.GetRange()

    timer.start("dist-collect-nodes")

    # collect nodes for the same task
    ntasks = int(sw.GetVar("gen_tasks"))
    Tasks = Snap.TIntIntVV(ntasks)

    Snap.IncVal(NewNodes, ds["first"])

    # assign nodes to tasks
    Snap.Nodes2Tasks1(NewNodes, Tasks, tsize)

    timer.stop("dist-collect-nodes")

    # send the messages
    timer.start("dist-send-all")
    for i in range(0,Tasks.Len()):
        Vec1 = Tasks.GetVal(i)
        if Vec1.Len() <= 0:
            continue

        # add task# at the end
        Vec1.Add(distance)
        sw.cum_timer.cum_start("network")
        sw.Send(i,Vec1,swsnap=True)
        sw.cum_timer.cum_stop("network")
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

def SaveState(sw, ds):
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
    sw.cum_timer = perf.Timer(sw.log)
    GetDist(sw)
    sw.cum_timer.cum_print("disk")
    sw.cum_timer.cum_print("network")
    
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
        sys.stdout.write("[ERROR] Exception in GenDistCpp2.main()\n")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(2)
