import sys
import traceback

import snap as Snap
import swlib
from swlib import LazyStr

# distmean = 100
# distvar  = 15.0

distmean = 150
distvar  = 22.5

# distmean = 50
# distvar  = 10.0

# distmean = 8.0
# distvar  = 1.0

def GenStubs(sw):
    """
    determine degrees for all the nodes, generate the stubs and distribute them
    """
    seg_bits = int(sw.GetVar('seg_bits'))

    taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.log.debug("msglist: %s" % str(msglist))

    ntasks = int(sw.GetVar("gen_tasks"))
    sw.log.debug("__tasks__ %s\t%d" % (taskname, ntasks))

    for item in msglist:
        dmsg = sw.GetMsg(item)
        d = dmsg["body"]
        ns = d["s"]
        nrange = d["r"]

        sw.log.debug(LazyStr(lambda: "task: %s, args: %s, start: %d, range: %d" % \
                (taskname, str(d), ns, nrange)))

        # 1) Get degrees
        # determine node degrees
        DegV = Snap.TIntV(nrange)               # vector of vertices' degree
        Snap.GetDegrees(DegV,distmean,distvar)  # populate

        # 2) Assign stubs
        # randomly assign stubs to tasks
        Tasks = Snap.TIntVVV(ntasks)  # vector of tasks, with each cell a segmented vector for nodes

        sw.log.debug("[%s] about to assign some random tasks" % taskname)

        # incrementing by ns is handled in this function
        Snap.AssignRndTask64(DegV, Tasks, ns, seg_bits) # each task is assigned a vec of vertex ids
        sw.log.debug("[%s] done assigning some random tasks" % taskname)
        # we have to add ns in the step above since otherwise
        # we would have to copy vectors

        # 3) Incremented base (above)
        # add ns to all values in Tasks
        # (handled in AssignRndTask64)

        # send messages
        for i in xrange(0,Tasks.Len()):
            sw.log.debug(LazyStr(lambda: "[%s] sending task %d, memsize %d" % \
                (taskname, i, Snap.GetMemSize64(Tasks.GetVal(i)))))
            sw.Send(i,Tasks.GetVal(i),swsnap=True)

def Worker(sw):
    GenStubs(sw)

def main():
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    fname = "swwork-%s.log" % (sw.GetName())

    sw.SetLog(fname)
    sw.GetConfig()

    Snap.SeedRandom()
    Worker(sw)

    sw.log.debug("finished")

if __name__ == '__main__':

    try:
        main()
    except:
        sys.stdout.write("[ERROR] Exception in GenStubsCpp.main()\n")
        traceback.print_exc(file=sys.stdout)
        sys.stdout.flush()
        sys.exit(2)

