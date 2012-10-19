import os
import sys

import swlib

#- init
#    - restore state
#    - get config
#- while persistent:
#    - while True:
#        - get input
#        - if no input:
#            break
#        - process input, produce output
#    - wait for host

def GenTasks(sw):
    """
    generate the tasks
        tname, task name
        nnodes, number of nodes
        tsize, number of nodes per task
    """

    taskname = sw.GetName()
    nnodes = int(sw.GetVar("nodes"))
    tsize = int(sw.GetVar("range"))
    flog.write("task %s, nodes %d, tsize %d\n" % (taskname, nnodes, tsize))
    flog.flush()

    ns = 0
    tc = 0
    while ns < nnodes:
        tname = tc
        ne = ns + tsize
        if ne > nnodes:
            ne = nnodes

        dout = {}
        dout["s"] = ns
        dout["e"] = ne-1

        sw.Send(tname,dout)

        tc += 1
        ns = ne

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    #flog = sys.stdout
    fname = "log-swwork-%s.txt" % (sw.GetName())
    flog = open(fname,"w")

    sw.SetLog(flog)
    sw.GetConfig()

    msgin = sw.GetInput()
    flog.write("msgin " + str(msgin) + "\n")
    flog.flush()

    for item in msgin:
        GenTasks(sw)

