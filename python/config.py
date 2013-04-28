import errno
import os
import sys

def readconfig(fname):

    dconf = {}
    f = open(fname)
    for line in f:
        cline = line.strip()
        #print cline

        words = cline.split()

        # skip empty lines and comments
        if len(words) == 0  or  words[0] == "#":
            continue

        #print words

        key = words[0]

        if key == "master":
            if len(words) < 2:
                continue
            value = words[1]

            w = value.split(":")
            if len(w) <= 0:
                continue
            h = w[0]
            p = "8080"
            if len(w) > 1:
                p = w[1]
            d = {}
            d["host"] = h
            d["port"] = p

            dconf["master"] = d

        elif key == "hosts":
            if len(words) < 2:
                continue
            value = words[1]

            hcount = 1
            if dconf.has_key("hosts"):
                hcount = len(dconf["hosts"]) + 1

            hosts = value.split(",")
            l = []
            for host in hosts:
                w = host.split(":")
                if len(w) <= 0:
                    continue
                h = w[0]
                p = "8100"
                if len(w) > 1:
                    p = w[1]
                d = {}
                d["host"] = h
                d["port"] = p
                d["id"] = str(hcount)
                l.append(d)
                hcount += 1
    
            if not dconf.has_key("hosts"):
                dconf["hosts"] = l
            else:
                dconf["hosts"].extend(l)

        elif key == "var":
            if len(words) < 3:
                continue
            name = words[1]
            value = words[2].replace(",","")

            if not dconf.has_key("var"):
                dconf["var"] = {}

            dconf["var"][name] = value

        elif key == "bunch":
            if len(words) < 6  or  words[2] != "size"  or  words[4] != "range":
                continue
            name = words[1]
            size = words[3]
            range = words[5]

            execprog = None
            if len(words) >= 8  and  words[6] == "exec":
                execprog = words[7]

            if size[0] == "$":
                size = dconf["var"][size[1:]]

            if range[0] == "$":
                range = dconf["var"][range[1:]]

            if execprog  and  len(execprog) > 0  and  range[0] == "$":
                execprog = dconf["var"][execprog[1:]]

            if not dconf.has_key("bunch"):
                dconf["bunch"] = {}

            dconf["bunch"][name] = {}
            dconf["bunch"][name]["size"] = size
            dconf["bunch"][name]["range"] = range
            if execprog:
                dconf["bunch"][name]["exec"] = execprog

        elif key == "route":
            if len(words) < 3:
                continue
            src = words[1]
            dest = words[2]

            srcname = src
            srcport = "1"
            srcwords = src.split(":")
            if len(srcwords) >= 2:
                srcname = srcwords[0]
                srcport = srcwords[1]

            if not dconf.has_key("route"):
                dconf["route"] = {}

            if not dconf["route"].has_key(srcport):
                dconf["route"][srcport] = {}

            dconf["route"][srcport][srcname] = dest

        elif key == "init":
            dconf["init"] = words[1]

    f.close()

    return dconf

def assign(dconf):
    hosts = dconf["hosts"]

    hostindex = 0
    dtasks = {}

    # add the initial task
    #hostindex = addtask(dtasks,hosts,"__Start__",hostindex)

    # assign all the task in round-robin fashion
    for bunch,bdata in dconf["bunch"].iteritems():
        #print bunch,bdata
        size = bdata["size"]
        #print bunch,size

        for i in xrange(0,int(size)):
            taskname = bunch + "-" + str(i)
            if bunch == "__Finish__":
                continue
            hostindex = addtask(dtasks,hosts,taskname,hostindex)

    # schedule the finish task on the first host
    addtask(dtasks,hosts,"__Finish__-0",0)
    return dtasks

def addtask(dtasks,hosts,taskname,hostindex):
    #print taskname, hosts[hostindex]
    dtasks[taskname] = hosts[hostindex]["id"]
    hostindex += 1
    if hostindex >= len(hosts):
        hostindex = 0

    return hostindex

def uniquefile(fpath):

    # find path, suffix ('/path/file', '.ext')
    fparts = os.path.splitext(fpath)

    fname = fpath
    
    counter = 1
    while 1:
        try:
            fd = os.open(fname, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            return os.fdopen(fd,"w"), fname
        except OSError:
            pass
        fname = fparts[0] + '_' + str(counter) + fparts[1]
        counter += 1

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: %s <file>" % (sys.argv[0])
        sys.exit(1)

    fname = sys.argv[1]

    # read the configuration file
    dconf = readconfig(fname)

    for key,value in dconf.iteritems():
        print "%s: %s" % (key, str(value))

    # assign tasks to hosts
    dtasks = assign(dconf)

    for key,value in dtasks.iteritems():
        print "%s: %s" % (key, str(value))

