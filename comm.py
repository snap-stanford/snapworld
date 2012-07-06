tmail = {}
tmail1 = {}

ntasks = 0

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

def mexec(func):
    print tmail1
    for task,args in tmail1.iteritems():
        print task, args
        func(task,args)

def msettasks(n):
    global ntasks
    ntasks = n

def mgettasks():
    return ntasks

