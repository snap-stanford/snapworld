import simplejson
import sys

def readconfig(fname):

    dconf = {}
    f = open(fname)
    for line in f:
        cline = line.split("\n")[0]
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
            dconf["master"] = value

        elif key == "hosts":
            if len(words) < 2:
                continue
            value = words[1]

            hosts = value.split(",")
            dconf["hosts"] = hosts

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

            if size[0] == "$":
                size = dconf["var"][size[1:]]

            if range[0] == "$":
                range = dconf["var"][range[1:]]

            if not dconf.has_key("bunch"):
                dconf["bunch"] = {}

            dconf["bunch"][name] = {}
            dconf["bunch"][name]["size"] = size
            dconf["bunch"][name]["range"] = range

        elif key == "route":
            if len(words) < 3:
                continue
            src = words[1]
            dest = words[2]

            if not dconf.has_key("route"):
                dconf["route"] = {}

            dconf["route"][src] = dest

    f.close()

    return dconf

def assign(dconf):
    hosts = dconf["hosts"]

    hostindex = 0
    dtasks = {}

    # add the initial task
    hostindex = addtask(dtasks,hosts,"__Start__",hostindex)

    # assign all the task in round-robin fashion
    for bunch,bdata in dconf["bunch"].iteritems():
        #print bunch,bdata
        size = bdata["size"]
        #print bunch,size

        for i in xrange(0,int(size)):
            taskname = bunch + "," + str(i)
            hostindex = addtask(dtasks,hosts,taskname,hostindex)

    return dtasks

def addtask(dtasks,hosts,taskname,hostindex):
    #print taskname, hosts[hostindex]
    dtasks[taskname] = hosts[hostindex]
    hostindex += 1
    if hostindex >= len(hosts):
        hostindex = 0

    return hostindex

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print "Usage: %s <file>" % (sys.argv[0])
        sys.exit(1)

    fname = sys.argv[1]

    # read the configuration file
    dconf = readconfig(fname)

    for key,value in dconf.iteritems():
        print "%s: %s" % (key, str(value))

    #print
    #json = simplejson.dumps(dconf)
    #print json
    
    # assign tasks to hosts
    dtasks = assign(dconf)

    for key,value in dtasks.iteritems():
        print "%s: %s" % (key, str(value))

