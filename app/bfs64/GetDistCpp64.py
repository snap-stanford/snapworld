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

    #taskname = sw.GetName()
    #taskindex = int(taskname.split("-")[1])
    taskindex = sw.GetIndex()

    sw.cum_timer.cum_start("disk")

    msglist = sw.GetMsgList()
    sw.log.debug("msglist: %s" % msglist)

    with perf.Timer(sw.log, "LoadState-GetDistCpp"):
        ds = LoadState(sw)

    sw.cum_timer.cum_stop("disk")

    # process initialization
    if ds == None:

        # first iteration: input is the source node
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
    node = None # TODO (smacke): ^^^ ???
    sw.cum_timer.cum_start("disk")
    for item in msglist:
        msg = sw.GetMsg(item)
        d = msg["body"]
    sw.cum_timer.cum_stop("disk")

    ns = d["s"]
    nrange = d["r"] # we don't use sw.GetRange() since this could be truncated I guess
    node = d.get("source",-1)

    ds = {}
    ds["first"] = ns
    ds["range"] = nrange
    ds["count"] = 0 # no. of visited nodes, since Visited is bitset-like vector
    ds["dist"] = 0
    ds["source"] = node
    
    seg_bits = int(sw.GetVar('seg_bits'))

    Visited = Snap.TIntV(nrange) # This also stores distances
    Snap.ZeroVec(Visited)
    if node >= 0:
        # set start node to 1, reset to 0 at the end
        # TODO (smacke): the reason we're doing this is because
        # the visited vec stores distances, but a "0" means not
        # visited yet. It would be better to make -1 mean not
        # visited yet so that we don't have this weird edge case

        Visited.GetVal(Snap.trailing(node-ns,seg_bits)).Val = 1
        # Also, why use GetVal when SetVal preserves semantic meaning?
        ds["count"] = 1

    ds["visit"] = Visited

    tsize = sw.GetRange()
    taskNumber = TaskId(node,tsize) # TODO (smacke): these really need to be named better

    # send the message
    if node >= 0:
        sw.log.debug('[%s] sending source node %d' % (sw.GetName(), node))
        Vec1 = Snap.TIntV()
        Vec1.Add(Snap.trailing(node,seg_bits))
        Vec1.Add(0) # this is the distance from source node to source node
        sw.Send(taskNumber,Vec1,swsnap=True) # send to GetNbrCpp64

    return ds

def AddNewNodes(taskindex, sw, ds, msglist):

    # all the nodes were visited already
    if ds["count"] >= ds["range"]:
        return

    distance = -1 # TODO (smacke): does this do anything? Maybe if we have no messages?
    Visited = ds["visit"]
    
    seg_bits = int(sw.GetVar('seg_bits'))
    this_segment_start = Snap.zeroLowOrderBits(ds['first'], seg_bits)
    sw.log.debug('this task starts at node %d' % ds['first'])
    sw.log.debug('this segment starts at node %d' % this_segment_start)

    timer = perf.Timer(sw.log)
    
    # nodes to add are on the input
    NewNodes = Snap.TIntV() # TODO (smacke): I think this is fine non-segmented

    timer.start("dist-msglist-iter")

    perf.DirSize(sw.log, sw.qin, "GetDist-qin")

    for item in msglist:

        sw.cum_timer.cum_start("disk")

        name = sw.GetMsgName(item)

        # read the input nodes
        FIn = Snap.TFIn(Snap.TStr(name))
        FringeSubset = Snap.TIntV(FIn)

        sw.cum_timer.cum_stop("disk")

        # it's okay to reassign and then use this later outside of the loop
        # since BSP should guarantee that this is the same at every loop iteration
        distance = FringeSubset.Last().Val + 1 # last value has prev distance, so we inc by 1
        FringeSubset.DelLast()

        # subtract the starting index
        sw.log.debug('[%s] offsetting by first node id' % sw.GetName())
        Snap.IncVal(FringeSubset, -(ds["first"] - this_segment_start))

        # get new nodes, not visited before
        # timer.start("dist-nodes-iter")
        
        # NewNodes will each have the segmented bits zero'd out, as well as
        # the high-order bits for this task
        sw.log.debug('[%s] calling GetNewNodes1' % sw.GetName())
        Snap.GetNewNodes1(FringeSubset, Visited, NewNodes, distance);
        # timer.stop("dist-nodes-iter")

    timer.stop("dist-msglist-iter")

    ds["dist"] = distance
    # This should never be -1 after processing message

    if distance==-1:
        sw.log.warn("[%s] thinks that the current distance is -1, \
        this almost certainly means that things are broken!" % sw.GetName())
    
    nnodes = ds["range"]
    ds["count"] += NewNodes.Len() # no. of new things we visited


    sw.log.info("distance: %d, new: %d, count: %d, nodes: %d" % \
            (distance, NewNodes.Len(), ds["count"], nnodes))

    sw.log.debug("testing: %d %d %d" % \
            (ds["count"], nnodes, ds["count"] >= nnodes))

    # done, no new nodes
    if ds["count"] >= nnodes:

        sw.log.debug("sending finish output")

        if ds["source"] >= 0:
            # reset start node to 0
            Visited.GetVal(ds["source"]-ds["first"]).Val = 0 # SMACKE: should be ok

        # get distance distribution, assume 1000 is the max
        DistCount = Snap.TIntV(1000)
        Snap.ZeroVec(DistCount)
        Snap.GetDistances(Visited,DistCount)

        # get the maximum positive distance
        maxdist = DistCount.Len()-1
        while (maxdist > 0) and (DistCount.GetVal(maxdist).Val == 0):
            maxdist -= 1

        maxdist += 1

        sw.log.debug("maxdist: %d" % maxdist)

        # collect the distances
        l = []
        for i in xrange(maxdist):
            # if DistCount.GetVal(i).Val <= 0: break
            l.append(DistCount.GetVal(i).Val)

        dmsg = {}
        dmsg["start"] = ds["source"]
        dmsg["dist"] = l

        dmsgout = {}
        dmsgout["src"] = sw.GetName()
        dmsgout["cmd"] = "results"
        dmsgout["body"] = dmsg

        sw.cum_timer.cum_start("network")
        sw.Send(0,dmsgout,"2")
        sw.cum_timer.cum_stop("network")

        sw.log.debug("final: %s %s" % (str(ds["source"]), str(distance)))
        sw.log.debug("distances: %s" % str(l))

    # nodes in each task
    tsize = sw.GetRange()

    timer.start("dist-collect-nodes")

    # collect nodes for the same task
    ntasks = int(sw.GetVar("gen_tasks"))
    Tasks = Snap.TIntIntVV(ntasks)
    # we will only ever send to tasks in the same segment, but
    # the wasted space shouldn't hurt that much

    sw.log.debug('[%s] increase nodes to within-segment values now' % sw.GetName())
    Snap.IncVal(NewNodes, ds["first"] - this_segment_start)

    # assign nodes to tasks
    sw.log.debug('[%s] calling Nodes2Tasks1' % sw.GetName())
    Snap.Nodes2Tasks1(NewNodes, Tasks, tsize)
    # All of the GetNbr tasks are in the same segment as this task
    # so this should still work; we just have to find the base task for
    # this segment and add it to all of the task indexes in Tasks

    timer.stop("dist-collect-nodes")

    # send the messages
    timer.start("dist-send-all")
    for i in xrange(Tasks.Len()):
        Vec1 = Tasks.GetVal(i)
        sw.log.debug('Vec1 length: %d' % Vec1.Len())
        if Vec1.Len() <= 0:
            continue

        # add task# at the end # TODO (smacke): I still don't understand this terminology
        Vec1.Add(distance)
        sw.cum_timer.cum_start("network")
        # we need to send to the correct segment, from which our
        # tasks are offset
        sw.Send(i + this_segment_start/tsize, Vec1, swsnap=True)
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
    ds["source"] = Start.Val
    ds["visit"] = Visited
    return ds

def SaveState(sw, ds):
    fname = sw.GetStateName()

    First = Snap.TInt(ds["first"])
    Range = Snap.TInt(ds["range"])
    Count = Snap.TInt(ds["count"])
    Dist = Snap.TInt(ds["dist"])
    Start = Snap.TInt(ds["source"])
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
        traceback.print_exc(file=sys.stdout, level=logging.DEBUG)
        sys.stdout.flush()
        sys.exit(2)
