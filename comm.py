# output message queue for the current step
tmail = {}
# input message queue for the current step
tmail1 = {}

# dispatch table from task names to functions, iterators
dispatch = {}

# table of iterators
diter = {}

# configuration table for global parameters
mconfig = {}

def msend(cmd, args):
    """
    send a message to task master
        cmd, command
        args, arguments as a string
    """

    print "*master* %s .%s." % (cmd, args)

    if cmd == "done":
        mswitch()

def mroute(tsrc, tdst, args):
    """
    send a message to the message router
        tsrc, source task name
        tdst, destination task name
        args, arguments as a string
    """
    global tmail

    print "*router* %s %s .%s." % (tsrc, tdst, args)

    #print "tmain-in", tmail

    if not tmail.has_key(tdst):
        tmail[tdst] = []

    tmail[tdst].append(args)

    #print "tmain-out", tmail

def mclear():
    global tmail
    tmail = {}

def mswitch():
    global tmail
    global tmail1

    tmail1 = tmail
    mclear()

def mexec():
    global dispatch
    global diter

    print tmail1

    # move the output queue to input queue, empty the output queue
    mswitch()

    # call all the tasks with their input queues
    for tname,args in tmail1.iteritems():
        print tname, args
        tval = dispatch[tname[0]]
        ftype = tval["type"]
        fname = tval["def"]

        if ftype == "func":
            # a function with no state, just call
            fname(tname,args)

        elif ftype == "iter":
            # an iterator with state, create it if it does not exist
            iname = tname.split("-")[0]
            if not diter.has_key(iname):
                diter[iname] = fname(tname,args)

            # perform the next step
            diter[iname].next()

def mgetargs(tname):
    global tmail1
    args = tmail1.get(tname,None)
    return args

def msetconfig(key,value):
    global mconfig
    mconfig[key] = value

def mgetconfig(key):
    global mconfig
    return mconfig.get(key,None)

def msetdispatch(disp):
    global dispatch
    dispatch = disp

