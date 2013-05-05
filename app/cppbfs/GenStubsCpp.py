import os
import sys
import traceback

import snap as Snap
import swlib

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

        sw.log.debug("task: %s, args: %s, start: %d, range: %d" % (taskname, str(d), ns, nrange))

        # determine node degrees
        DegV = Snap.TIntV(nrange)
        Snap.GetDegrees(DegV,distmean,distvar)

        # 1: got degrees (above)

        # randomly assign stubs to tasks
        Tasks = Snap.TIntIntVV(ntasks)
        Snap.AssignRndTask(DegV, Tasks)

        # 2: assigned stubs (above)

        # add ns to all values in Tasks
        for i in xrange(0,Tasks.Len()):
            Snap.IncVal(Tasks.GetVal(i), ns)

        # 3: incremented base (above)

        # send messages
        for i in xrange(0,Tasks.Len()):
            sw.log.debug("sending task %d, len %d" % \
                    (i, Tasks.GetVal(i).Len()))
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

