import client
import os
import sys
import json
import logging

gotsnap = False

try:
    import snap as Snap
    gotsnap = True
except:
    pass

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
        self.log = None
        self.log_filename = None
        
    def SetLog(self, filename, level=logging.INFO):
        self.log_filename = filename
        self.log = logging.getLogger(self.log_filename)
        self.log.setLevel(level)
        fh = logging.FileHandler(filename)
        fh.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s'))
        self.log.addHandler(fh)

    def GetLog(self):
        return self.log_filename

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

        self.config = json.loads(sconf)

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

        self.log.debug("Configuration: %s" % str(self.config))
        self.log.debug("config size %d" % (len(str(self.config))))

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
        msg = json.loads(s)
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
        d = json.loads(s)

        return d

    def SaveState(self, d):
        # save the state
        fname = "swstate-%s.txt" % (self.taskname)

        f = open(fname,"w")
        s = json.dumps(d)
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
            if not gotsnap:
                self.log.error("Snap module is not available")
                sys.exit(2)
                
            # Snap vector
            if self.local:
                FOut = Snap.TFOut(Snap.TStr(fname))
                d.Save(FOut)
                FOut.Flush()
                #print "send Snap task %s, host %s, *** Error: local 'Send' not yet implemented" % (dstname, dshost)
                return

            client.messagevec(dshost,self.taskname,dstname,d)
            return
     
        else:
            # json dict
            s = json.dumps(d)
            # print "send task %s, host %s, msg %s" % (dstname, dshost, s)

            if self.local:
                f = open(fname,"w")
                f.write(s)
                f.close()
                return

            client.message(dshost,self.taskname,dstname,s)

