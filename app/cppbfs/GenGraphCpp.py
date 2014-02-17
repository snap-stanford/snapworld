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

def SelectNodes(sw):
    """
    select random nodes for distance calculations
    """

    # generate samples in the first task ...-0
    taskname = sw.GetName()
    index = taskname.split("-")
    if len(index) < 2  or  index[1] != "0":
        return

    # get all the nodes and the number of samples
    nnodes = int(sw.GetVar("nodes"))
    nsample = int(sw.GetVar("stat_tasks"))

    s = set()
    # TODO (smacke): this is only here for debug purposes
    random.seed(0)
    for i in xrange(0, nsample):
        while 1:
            n = int(random.random() * nnodes)
            if not n in s:
                break
        sw.Send(i,n,"2")
        s.add(n)

def GenGraph(sw):
    """
    generate the graph edges
    """

    # extract the stubs from the args
    # iterate through the input queue and add new items to the stub list

    # taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.log.debug("msglist: %s" % msglist)

    Stubs = Snap.TIntV() # Stubs is an empty vector
    for item in msglist:

        # 1) Get item in msglist

        # 2) Get name of item
        name = sw.GetMsgName(item)

        # 3) Get vector associated with name
        FIn = Snap.TFIn(Snap.TStr(name))
        Vec = Snap.TIntV(FIn)

        # 4) Add vector to Stubs
        Stubs.AddV(Vec)

    # 5) Got all stubs, which is of length msglist

    # Randomize the items (aka shuffle)
    Snap.Randomize(Stubs)

    # nodes in each task and the number of tasks
    tsize = sw.GetRange()
    ntasks = int(sw.GetVar("gen_tasks"))

    # get edges for a specific task
    Tasks = Snap.TIntIntVV(ntasks)  # vector of length ntasks containing vectors
    Snap.AssignEdges(Stubs, Tasks, tsize)

    # send messages
    for i in xrange(0,Tasks.Len()):
        sw.log.debug("sending task: %d, len: %d" % (i, Tasks.GetVal(i).Len()))
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

