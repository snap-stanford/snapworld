import os
import random
import sys

import snap as Snap
import swlib

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

def GetNeighbors(sw, AdjLists, Nodes):
    # report node neighbors

    # the last value is the distance
    dist = Nodes.Last().Val
    Nodes.DelLast()

    Hood = Snap.TIntV()
    Snap.GetNeighborhood(Nodes, AdjLists, Hood);

    print "Hood len %d" % (Hood.Len())

    # nodes in each task
    tsize = sw.GetRange()

    # collect nodes for the same task
    ntasks = int(sw.GetVar("stat_tasks"))
    Tasks = Snap.TIntIntVV(ntasks)

    # assign nodes to tasks
    Snap.Nodes2Tasks1(Hood, Tasks, tsize)

    # send the messages
    for i in range(0,Tasks.Len()):
        Vec1 = Tasks.GetVal(i)
        if Vec1.Len() <= 0:
            continue

        # add distance at the end
        Vec1.Add(dist)
        sw.Send(i,Vec1,swsnap=True)

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

