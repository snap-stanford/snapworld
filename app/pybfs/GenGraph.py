import random
import sys

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
    for i in range(0, nsample):
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

    taskname = sw.GetName()

    msglist = sw.GetMsgList()
    sw.log.debug("msglist " + str(msglist))

    stubs = []
    for item in msglist:
        dmsg = sw.GetMsg(item)
        msg = dmsg["body"]
        sw.log.debug("task %s, args %s" % (taskname, str(msg)))

        stubs.extend(msg)

    #print taskname,stubs

    # randomize the items
    random.shuffle(stubs)
    #print taskname + "-r",stubs

    # get the pairs
    pairs = zip(stubs[::2], stubs[1::2])
    #print taskname,pairs

    # nodes in each task
    tsize = sw.GetRange()

    # get edges for a specific task
    edges = {}
    for pair in pairs:
        esrc = pair[0]
        edst = pair[1]

        # add the edge twice for both directions
        tdst = TaskId(esrc, tsize)
        if not edges.has_key(tdst):
            edges[tdst] = []
        l = [esrc, edst]
        edges[tdst].append(l)

        tdst = TaskId(edst, tsize)
        if not edges.has_key(tdst):
            edges[tdst] = []
        l = [edst, esrc]
        edges[tdst].append(l)

    #print taskname,edges

    dmsgout = {}
    dmsgout["src"] = taskname
    dmsgout["cmd"] = "init"

    for tdst, msgout in edges.iteritems():
        sw.log.debug("sending task %d, msg %s" % (tdst, str(msgout)))
        dmsgout["body"] = msgout
        sw.Send(tdst, dmsgout)

def Worker(sw):
    #SelectNodes(sw)
    GenGraph(sw)

if __name__ == '__main__':
    
    sw = swlib.SnapWorld()
    sw.Args(sys.argv)

    fname = "swwork-%s.log" % (sw.GetName())

    sw.SetLog(fname)
    sw.GetConfig()

    Worker(sw)

    sw.log.info("finished")

