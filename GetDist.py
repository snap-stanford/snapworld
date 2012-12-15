import os
import random
import sys

import swlib

def TaskId(node,tsize):
    """
    return the task id for a node
    """

    return node/tsize

def GetDist(sw):
    """
    find the node distance
    """

    taskname = sw.GetName()
    taskindex = taskname.split("-")[1]

    msglist = sw.GetMsgList()
    sw.flog.write("msglist " + str(msglist) + "\n")
    sw.flog.flush()

    ds = sw.LoadState()

    # process initialization
    if ds == None:

        # first iteration: input is the start node
        ds = InitState(taskindex, msglist)

    else:
        # successive iterations: input are the new nodes
        AddNewNodes(taskindex, sw, ds, msglist)

    sw.SaveState(ds)

def InitState(taskindex, msglist):

    # the original node is on input
    node = None
    for item in msglist:
        node = sw.GetMsg(item)

    snode = str(node)

    ds = {}
    ds["start"] = snode
    ds["dist"] = 0

    ds["visit"] = {}
    ds["visit"][snode] = 0

    tsize = sw.GetRange()
    tn = TaskId(node,tsize)

    dmsg = {}
    dmsg["task"] = taskindex
    dmsg["nodes"] = [node]
    sw.Send(tn,dmsg)

    return ds

def AddNewNodes(taskindex, sw, ds, msglist):

    ds["dist"] += 1
    distance = ds["dist"]
    visited = ds["visit"]
    
    # nodes to add are on the input
    newnodes = set()
    for item in msglist:
        nodes = sw.GetMsg(item)
        for node in nodes:
            snode = str(node)
            if snode in visited:
                continue
            newnodes.add(node)
            visited[snode] = distance

    # done, no new nodes
    if len(newnodes) <= 0:
        # get distance distribution
        dcount = {}
        for snode,distance in visited.iteritems():
            if not dcount.has_key(distance):
                dcount[distance] = 0
            dcount[distance] += 1

        nnodes = int(sw.GetVar("nodes"))
        l = []
        for i in range(0, nnodes):
            if not dcount.has_key(i):
                break
            l.append(dcount[i])

        sw.flog.write("final " + ds["start"] + " " + str(distance) + " " + str(visited) + "\n")
        sw.flog.write("distances " + str(l) + "\n")
        sw.flog.flush()
        return

    # nodes in each task
    tsize = sw.GetRange()

    # collect nodes for the same task
    dtasks = {}
    for ndst in newnodes:
        tn = TaskId(ndst,tsize)
        if not dtasks.has_key(tn):
            dtasks[tn] = []
        dtasks[tn].append(ndst)

    #print "dtasks", dtasks

    # send the messages
    for tn,args in dtasks.iteritems():
        dmsg = {}
        dmsg["task"] = taskindex
        dmsg["nodes"] = args
        sw.Send(tn,dmsg)

def Worker(sw):
    GetDist(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    #flog = sys.stdout
    fname = "log-swwork-%s.txt" % (sw.GetName())
    flog = open(fname,"w")

    sw.SetLog(flog)
    sw.GetConfig()

    Worker(sw)

    flog.write("finished\n")
    flog.flush()

