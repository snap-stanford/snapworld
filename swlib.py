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
        self.range = None

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

        dbunch = self.config.get("bunch")
        hostlist = self.config.get("hosts")

        if dbunch:
            dinfo = dbunch.get(self.name)
            if dinfo:
                self.range = int(dinfo.get("range"))

        if self.route:
            for key, routes in self.route.iteritems():
                dest = routes.get(self.name)
                if dest:
                    if not target:
                        self.target = {}
                    self.target[key] = dest

        if (self.var   == None  or  self.route  == None  or
            hostlist   == None  or  self.tasks  == None  or
            self.range == None  or  self.target == None):
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

    def GetRange(self):
        return self.range

    def GetMsgList(self):
        l = os.listdir(self.qin)
        return l

    def GetMsg(self, name):
        msgpath = os.path.join(self.qin, name)
        f = open(msgpath, "r")
        result = f.read()
        f.close()
        return result

    def GetVar(self, name):
        # get variables from the configuration
        # get the variable requested
        result = self.var.get(name)
        return result

    def LoadState(self, d):
        return None

    def SaveState(self, d):
        pass

    def Send(self, dstid, d):
        #dstnum = dstid / self.range
        #dstname = self.target + "-" + str(dstnum)
        dstname = self.target["1"] + "-" + str(dstid)
        dsthostid = self.tasks.get(dstname)
        dshost = self.hosts.get(dsthostid)

        s = simplejson.dumps(d)
        print "send  task %s, host %s, msg %s" % (dstname, dshost, s)

        client.message(dshost,self.taskname,dstname,s)

