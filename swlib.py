import client
import os
import simplejson
import sys

import snap as Snap

class SnapWorld:
    def __init__(self):
        pass

    def Args(self, argv):
        if len(argv) < 7:
            print "Usage: " + argv[0] + " -t <id> -h <host>:<port> -q <queue_dir> -c <config_file> -l"
            sys.exit(1)

        self.taskname = None
        self.host = None
        self.qin = None
        self.configfile = None
        self.local = False

        index = 1
        while index < len(argv):
            arg = argv[index]
            if arg == "-t":
                # task name
                index += 1
                self.taskname = argv[index]
            elif arg == "-h":
                # host process address
                index += 1
                self.host = argv[index]
            elif arg == "-q":
                # input queue location
                index += 1
                self.qin = argv[index]
            elif arg == "-c":
                # config file name (optional, needed if local)
                index += 1
                self.configfile = argv[index]
            elif arg == "-l":
                # local operation, no network
                self.local = True

            index += 1

        if (self.taskname == None  or  self.qin == None  or
            (self.host == None  and  self.configfile == None)):
            print "Usage: " + argv[0] + " -t <id> -h <host>:<port> -q <queue_dir> -c <config_file> -l"
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

    def GetLog(self):
        return self.flog

    def GetConfig(self):
        # get configuration from the host
        sconf = None
        if self.configfile:
            try:
                f = open(self.configfile)
                sconf = f.read()
                f.close()
            except:
                pass
        elif self.host:
            sconf = client.config(self.host)

        if not sconf:
            print "*** no configuration"
            return None

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
                    if not self.target:
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

    def GetMsgName(self, name):
        msgname = os.path.join(self.qin, name)
        return msgname

    def GetMsg(self, name):
        msgpath = os.path.join(self.qin, name)
        f = open(msgpath, "r")
        s = f.read()
        f.close()
        msg = simplejson.loads(s)
        return msg

    def GetVar(self, name):
        # get variables from the configuration
        # get the variable requested
        result = self.var.get(name)
        return result

    def GetStateName(self):
        fname = "swstate-%s.txt" % (self.taskname)
        return fname
        
    def LoadState(self):
        fname = "swstate-%s.txt" % (self.taskname)

        try:
            f = open(fname,"r")
        except:
            return None

        s = f.read()
        f.close()
        d = simplejson.loads(s)

        return d

    def SaveState(self, d):
        # save the state
        fname = "swstate-%s.txt" % (self.taskname)

        f = open(fname,"w")
        s = simplejson.dumps(d)
        f.write(s)
        f.close()

    def GetOutName(self, dstname):
        fname = "swout-%s-%s.txt" % (self.taskname, dstname)
        return fname

    def Send(self, dstid, d, channel = "1", swsnap = False):

        #dstnum = dstid / self.range
        #dstname = self.target + "-" + str(dstnum)
        dstname = self.target[channel] + "-" + str(dstid)
        dsthostid = self.tasks.get(dstname)
        dshost = self.hosts.get(dsthostid)

        if self.local:
            fname = self.GetOutName(dstname)

        if swsnap:
            # Snap vector
            if self.local:
                FOut = Snap.TFOut(Snap.TStr(fname))
                d.Save(FOut)
                FOut.Flush()
                #print "send Snap task %s, host %s, *** Error: local 'Send' not yet implemented" % (dstname, dshost)
                return

            client.messagevec(dshost,self.taskname,dstname,d)

        else:
            # json dict
            s = simplejson.dumps(d)
            print "send  task %s, host %s, msg %s" % (dstname, dshost, s)

            if self.local:
                f = open(fname,"w")
                f.write(s)
                f.close()
                return

            client.message(dshost,self.taskname,dstname,s)

