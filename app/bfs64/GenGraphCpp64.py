import random
import sys
import traceback

import snap as Snap
import swlib

def TaskId(node,tsize):
    """
    return the task id for a node
    """

    return node/tsize

def GenGraph(sw):
    """
    generate the graph edges
    """

    # extract the stubs from the args
    # iterate through the input queue and add new items to the stub list

    # taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.log.debug("msglist: %s" % msglist)

    Stubs = Snap.TIntIntVV() # Stubs is an empty vector
    for item in msglist:

        # 1) Get item in msglist

        # 2) Get name of item
        name = sw.GetMsgName(item)

        # 3) Get vector associated with name
        FIn = Snap.TFIn(Snap.TStr(name))
        Vec64 = Snap.TIntIntVV(FIn)

        # 4) Add vector to Stubs
        #Stubs.AddV(Vec)
        Snap.AddVec64(Stubs, Vec64)

    # 5) Got all stubs, which is of length msglist

    # Randomize the items (aka shuffle)
    #Snap.Randomize(Stubs)

    # nodes in each task and the number of tasks
    tsize = sw.GetRange()
    seg_bits = int(sw.GetVar('seg_bits'))
    ntasks = int(sw.GetVar("gen_tasks"))

    # get edges for a specific task
    Tasks = Snap.TIntVVV(ntasks)  # vector of length ntasks containing vectors
    Snap.AssignRandomEdges64(Stubs, Tasks, tsize, seg_bits)
    #Snap.AssignEdges(Stubs, Tasks, tsize)

    # send messages
    for i in xrange(0,Tasks.Len()):
        # TODO (smacke): this logging doesn't make sense anymore since the
        # Len() here gives number of segments, not number of stubs
        #sw.log.debug("sending task: %d, len: %d" % (i, Tasks.GetVal(i).Len()))
        sw.Send(i,Tasks.GetVal(i),swsnap=True)

def Worker(sw):
    GenGraph(sw)

def main():    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    fname = "swwork-%s.log" % (sw.GetName())

    sw.SetLog(fname)
    sw.GetConfig()

    Snap.SeedRandom()
    Worker(sw)

    sw.log.info("finished")

if __name__ == '__main__':
    try:
        main()
    except:
        sys.stdout.write("[ERROR] Exception in GenGraphCpp.main()\n")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(2)

