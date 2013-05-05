import os
import random
import sys

import snap as Snap
import swlib

import perf

def GetNbr(sw):
    """
    provide graph neighbors
    """

    taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.log.debug("msglist %s" % str(msglist))

    AdjLists = None
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
    sw.log.debug("state %s" % str(AdjLists.Len()))
    
    with perf.Timer(sw.log, "SaveState-GetNbrCpp"):
        SaveState(sw, AdjLists)

    dmsgout = {}
    dmsgout["src"] = sw.GetName()
    dmsgout["cmd"] = "targets"
    dmsgout["body"] = {}
    sw.Send(0,dmsgout,"2")

def GetEdges(sw, Edges):

    sw.log.debug("edges %s" % str(Edges.Len()))

    AdjLists = Snap.TIntIntVH()
    Snap.GetAdjLists(Edges, AdjLists)

    return AdjLists

def GetNeighbors(sw, AdjLists, Nodes):
    # report node neighbors

    # the last value is the task
    tdst = Nodes.Last().Val
    Nodes.DelLast()

    Hood = Snap.TIntV()
    Snap.GetNeighborhood(Nodes, AdjLists, Hood);

    # print "Hood len %d" % (Hood.Len())

    sw.Send(tdst,Hood,swsnap=True)

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
    main()
