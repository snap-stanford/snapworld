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
    AdjLists = Snap.TIntIntVH(FIn)
    return AdjLists

def SaveState(AdjLists):
    fname = sw.GetStateName()
    FOut = Snap.TFOut(Snap.TStr(fname))
    AdjLists.Save(FOut)
    FOut.Flush()

def GetNbr(sw):
    """
    provide graph neighbors
    """

    taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.flog.write("msglist " + str(msglist) + "\n")
    sw.flog.flush()

    AdjLists = LoadState()

    if AdjLists:
        # state is available, process requests for neighbors
        # TODO: rewrite input message to SNAP format for GetDist
        for item in msglist:
            dmsg = sw.GetMsg(item)
            cmd = dmsg["cmd"]
            msg = dmsg["body"]

            GetNeighbors(sw, AdjLists, msg)
        return

    # state not found, initialize it with neighbors
    Edges = Snap.TIntV()

    for item in msglist:

        sw.flog.write("1 got item " + item + "\n")
        sw.flog.flush()

        name = sw.GetMsgName(item)

        sw.flog.write("2 got name " + name + "\n")
        sw.flog.flush()

        FIn = Snap.TFIn(Snap.TStr(name))
        Vec = Snap.TIntV(FIn)

        sw.flog.write("3 got vector %d" % (Vec.Len()) + "\n")
        sw.flog.flush()

        Edges.AddV(Vec)

    # first iteration: input are edges, save the state
    AdjLists = GetEdges(Edges)
    sw.flog.write("state " + str(AdjLists.Len()) + "\n")
    sw.flog.flush()

    SaveState(AdjLists)

    dmsgout = {}
    dmsgout["src"] = sw.GetName()
    dmsgout["cmd"] = "targets"
    dmsgout["body"] = {}
    sw.Send(0,dmsgout,"2")

def GetEdges(Edges):

    #print edges
    sw.flog.write("edges " + str(Edges.Len()) + "\n")
    sw.flog.flush()

    AdjLists = Snap.TIntIntVH()
    Snap.GetAdjLists(Edges, AdjLists)

    return AdjLists

def GetNeighbors(sw, AdjLists, msg):
    # report node neighbors

    tdst = msg["task"]
    nodes = msg["nodes"]
    s = set()
    for node in nodes:
        # TODO: rewrite for SNAP once GetDist is SNAP format
        Nbrs = AdjLists.GetDat(node)
        for j in range(0, Nbrs.Len()):
            s.add(Nbrs.GetVal(j).Val)

    print "s", str(s)
    # TODO: rewrite output message to SNAP format for GetDist
    dmsgout = {}
    dmsgout["src"] = sw.GetName()
    dmsgout["cmd"] = "nbrs"
    dmsgout["body"] = list(s)
    sw.Send(tdst,dmsgout)

def Worker(sw):
    GetNbr(sw)

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

