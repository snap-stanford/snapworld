import client
import os
import simplejson
import sys

class SnapWorld:
    def __init__(self):
        pass

    def Args(self, argv):
        if len(argv) < 7:
            print "Usage: " + argv[0] + " -t <id> -h <host>:<port> -q <queue_dir>"
            sys.exit(1)

        self.taskname = None
        self.host = None
        self.qin = None

        index = 1
        while index < len(argv):
            arg = argv[index]
            if arg == "-t":
                index += 1
                self.taskname = argv[index]
            elif arg == "-h":
                index += 1
                self.host = argv[index]
            elif arg == "-q":
                index += 1
                self.qin = argv[index]

            index += 1

        if self.taskname == None  or  self.host == None  or  self.qin == None:
            print "Usage: " + argv[0] + " -t <id> -h <host>:<port> -q <queue_dir>"
            sys.exit(1)

        self.config = None
        self.name = self.taskname.split("-",1)[0]

        self.var = None
        self.route = None
        self.hosts = None
        self.tasks = None

        self.target = None
        self.flog = None

    def SetLog(self, flog):
        self.flog = flog

        self.flog.write("Starting task %s with host %s, queue %s\n" % (self.taskname, self.host, self.qin))
        self.flog.flush()

    def GetConfig(self):
        # get configuration from the host
        sconf = client.config(self.host)
        self.config = simplejson.loads(sconf)

        self.var = self.config.get("var")
        self.route = self.config.get("route")
        self.tasks = self.config.get("tasks")
        hostlist = self.config.get("hosts")
        self.target = self.route.get(self.name)

        if (self.var == None  or  self.route == None  or
            hostlist == None  or  self.tasks == None  or
            self.target == None):
            return None

        self.hosts = {}
        for h in hostlist:
            self.hosts[h["id"]] = h["host"] + ":" + h["port"]

        self.flog.write(str(self.config))
        self.flog.write("\n")
        self.flog.write("Got configuration size %d\n" % (len(str(self.config))))
        self.flog.flush()

        return self.config

    def GetName(self):
        return self.taskname

    def GetHost(self):
        return self.host

    def GetInput(self):
        l = os.listdir(self.qin)
        return l

    def GetVar(self, name):
        # get variables from the configuration
        # get the variable requested
        result = self.var.get(name)
        return result

    def Send(self, dst, d):
        dstname = self.target + "-" + str(dst)
        dstid = self.tasks.get(dstname)
        dshost = self.hosts.get(dstid)

        s = simplejson.dumps(d)
        print "send  task %s, host %s, msg %s" % (dstname, dshost, s)

        client.message(dshost,self.taskname,dstname,s)

