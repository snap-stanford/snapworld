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

def mcontinue():
    global tmail1

    status = len(tmail) > 0
    return status

def mexec():
    global dispatch
    global diter

    #print tmail1

    # move the output queue to input queue, empty the output queue
    mswitch()

    print "tmail1"
    for key,value in tmail1.iteritems():
        print key, value

    # call all the tasks with their input queues
    for tname,args in tmail1.iteritems():
        print "mexec", tname, args
        tval = dispatch[tname[0]]
        ftype = tval["type"]
        fname = tval["def"]

        if ftype == "func":
            # a function with no state, just call
            fname(tname,args)

        elif ftype == "iter":
            # an iterator with state, create it if it does not exist
            iname = tname.split("-")[0]
            print "iname", iname
            print "diter1", diter
            if not diter.has_key(iname):
                print "iname", iname, "*new*"
                diter[iname] = fname(tname,args)

            #print diter
            # perform the next step
            try:
                diter[iname].next()
            except StopIteration:
                # remove the iterator
                #print "*StopIteration*"
                del diter[iname]

def mgetargs(tname):
    global tmail1
    args = tmail1.get(tname,None)
    print "args", tname, args
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

