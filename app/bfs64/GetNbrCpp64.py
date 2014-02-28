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

    taskname = sw.GetName()
    # tindex = sw.GetIndex()

    msglist = sw.GetMsgList()
    sw.log.debug("msglist %s" % msglist)

    with perf.Timer(sw.log, "LoadState-GetNbrCpp"):
        AdjLists = LoadState(sw)

    if AdjLists:
        # state is available, process requests for neighbors
        sw.log.debug('[%s] state available, length %d' % (sw.GetName(), AdjLists.Len()))
        for item in msglist:
            name = sw.GetMsgName(item)

            # read the input nodes
            FIn = Snap.TFIn(Snap.TStr(name))
            msg = Snap.TIntV(FIn)

            GetNeighbors(sw, AdjLists, msg)
        return

    # state not found, initialize it with neighbors
    sw.log.debug('[%s] adjlist not found, initializing' % sw.GetName())
    Edges = Snap.TIntIntVV()

    for item in msglist:
        name = sw.GetMsgName(item)

        FIn = Snap.TFIn(Snap.TStr(name))
        Vec = Snap.TIntIntVV(FIn)

        Snap.AddVec64(Edges, Vec)

    # first iteration: input are edges, save the state
    AdjLists = GetEdges(sw, Edges)

    sw.log.debug('[%s] saving adjlist of size %d now' % (sw.GetName(), AdjLists.Len()))
    
    with perf.Timer(sw.log, "SaveState-GetNbrCpp"):
        SaveState(sw, AdjLists)

    dmsgout = {}
    dmsgout["src"] = sw.GetName()
    dmsgout["cmd"] = "targets"
    dmsgout["body"] = {}
    sw.Send(0,dmsgout,"2")

def GetEdges(sw, Edges):

    sw.log.warn("edges: %d" % Edges.Len())

    #AdjLists = Snap.TIntIntVH()
    #Snap.GetAdjLists(Edges, AdjLists)
    AdjLists = Snap.TIntVVH();
    Snap.GetAdjLists64(Edges, AdjLists)

    return AdjLists

def GetNeighbors(sw, AdjLists, Nodes):
    # report node neighbors

    # the last value is the task
    # TODO (smacke): ^ I don't understand this comment
    dist = Nodes.Last().Val
    Nodes.DelLast()

    SegmentedHood = Snap.TIntIntVV()
    sw.log.warn('getting neighbors for %d nodes', Nodes.Len())
    Snap.GetNeighborhood64(Nodes, AdjLists, SegmentedHood);

    sw.log.warn("SegmentedHood len: %d" % SegmentedHood.Len())

    # TODO (smacke): I think this gets $drange, since
    # we are sending this to the GetDist task. Is there
    # any way to make this clearer in the config file?
    # Perhaps add in optional string argument to GetRange()
    # which takes a destination port number, so we don't
    # specify GetNbr range as $drange in the config.
    tsize = sw.GetRange()
    seg_bits = int(sw.GetVar('seg_bits'))

    # collect nodes for the same task
    ntasks = int(sw.GetVar("stat_tasks"))
    Tasks = Snap.TIntIntVV(ntasks) # this should be fine as long as (1<<seg_bits) is a multiple of drange

    # assign nodes to tasks
    #Snap.Nodes2Tasks1(SegmentedHood, Tasks, tsize)
    Snap.Nodes2Tasks64(SegmentedHood, Tasks, tsize, seg_bits)

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
    AdjLists = Snap.TIntVVH(FIn)
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
        sys.stdout.write("[ERROR] Exception in GetNbrCpp2.main()\n")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(2)

