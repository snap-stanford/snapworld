import os
import sys
import traceback

import snap as Snap
import swlib

import perf

def GetNbr(sw):
    """
    provide graph neighbors
    """

    # taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.log.debug("msglist %s" % msglist)

    with perf.Timer(sw.log, "LoadState-GetNbrCpp"):
        AdjLists = LoadState(sw)

    if AdjLists:
        # state is available, process requests for neighbors
        for item in msglist:
            name = sw.GetMsgName(item)

            # read the input nodes
            FIn = Snap.TFIn(Snap.TStr(name))
            msg = Snap.TIntV(FIn)

            GetNeighbors(sw, AdjLists, msg)
        return

    # state not found, initialize it with neighbors
    Edges = Snap.TIntV()

    for item in msglist:
        name = sw.GetMsgName(item)

        FIn = Snap.TFIn(Snap.TStr(name))
        Vec = Snap.TIntV(FIn)

        Edges.AddV(Vec)

    # first iteration: input are edges, save the state
    AdjLists = GetEdges(sw, Edges)
    sw.log.debug("state: %d" % AdjLists.Len())
    
    with perf.Timer(sw.log, "SaveState-GetNbrCpp"):
        SaveState(sw, AdjLists)

    dmsgout = {}
    dmsgout["src"] = sw.GetName()
    dmsgout["cmd"] = "targets"
    dmsgout["body"] = {}
    sw.Send(0,dmsgout,"2")

def GetEdges(sw, Edges):

    sw.log.debug("edges: %d" % Edges.Len())

    AdjLists = Snap.TIntIntVH()
    Snap.GetAdjLists(Edges, AdjLists)

    return AdjLists

def GetNeighbors(sw, AdjLists, Nodes):
    # report node neighbors

    # the last value is the task
    dist = Nodes.Last().Val
    Nodes.DelLast()

    Hood = Snap.TIntV()
    Snap.GetNeighborhood(Nodes, AdjLists, Hood);

    sw.log.debug("Hood len: %d" % Hood.Len())

    tsize = sw.GetRange()

    # collect nodes for the same task
    ntasks = int(sw.GetVar("stat_tasks"))
    Tasks = Snap.TIntIntVV(ntasks)

    # assign nodes to tasks
    Snap.Nodes2Tasks1(Hood, Tasks, tsize)

    # send the messages
    for i in xrange(Tasks.Len()):
        Vec1 = Tasks.GetVal(i)
        if Vec1.Len() <= 0:
            continue

        # add distance at the end
        Vec1.Add(dist)
        sw.Send(i,Vec1,swsnap=True)

def LoadState(sw):
    fname = sw.GetStateName()
    if not os.path.exists(fname):
        return None

    FIn = Snap.TFIn(Snap.TStr(fname))
    AdjLists = Snap.TIntIntVH(FIn)
    return AdjLists

def SaveState(sw, AdjLists):
    fname = sw.GetStateName()
    FOut = Snap.TFOut(Snap.TStr(fname))
    AdjLists.Save(FOut)
    FOut.Flush()

def Worker(sw):
    GetNbr(sw)

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
        sys.stdout.write("[ERROR] Exception in GetNbrCpp.main()\n")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(2)

