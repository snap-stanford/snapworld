tqueue = []

def msend(cmd, args):
    """
    send a message to task master
        cmd, command
        args, arguments as a string
    """

    print "*master* %s .%s." % (cmd, args)

    if cmd == "task":
        tqueue.append(args)

def mclear():
    tqueue = []

def mexec(func):
    for item in tqueue:
        func(item)

