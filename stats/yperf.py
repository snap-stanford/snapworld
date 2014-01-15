#
#   Field names:
#      cu, cpu user
#      cs, cpu system
#      ci, cpu idle
#      cw, cpu wait
#      cn, cpu interrupt
#
#      dr, disk read
#      dw, disk write
#
#      nr, network receive
#      nw, network write
#

import simplejson as json
import os
import resource
import sys
import time

class Logger:

    def __init__(self,dir,nameprefix):

        self.dir = dir
        self.nameprefix = nameprefix

        self.f = None
        self.name = None

    def write(self,t,msg):
        self.open(t)
        try:
            s = "%d\t%s\n" % (t, msg)
            self.f.write(s)
            self.f.flush()
        except:
            self.open(t)

    def close(self):
        self.f.close()

    def open(self, t):

        newname = self.getfname(t)
        if self.f  and  self.name == newname:
            return

        if self.f:
            self.f.close()

        self.name = newname
        self.f = open(self.name,"a")

    def getfname(self, t):
        """
        get log name, one file per day: <name>-<date>-<hour>.txt
        """

        tnow = t
        s = time.strftime("%Y%m%d-%H",time.localtime(tnow))
        result = self.nameprefix + "-" + s + ".txt"
        return result

def getstat():

    d = {}

    #
    #   get CPU statistics
    #

    fcpu = open("/proc/stat")
    content = fcpu.read()
    fcpu.close()

    #print content

    lines = content.splitlines()
    for line in lines:
        words = line.split()
        if words[0] == "cpu":
            break

    d["cu"] = long(words[1]) + long(words[2])
    d["cu"] = long(words[1]) + long(words[2])
    d["cs"] = long(words[3])
    d["ci"] = long(words[4])
    d["cw"] = long(words[5])
    d["cn"] = long(words[6]) + long(words[7])

    #
    #   get disk statistics
    #

    fdisk = open("/proc/diskstats")
    content = fdisk.read()
    fdisk.close()

    #print content

    lines = content.splitlines()
    for line in lines:
        words = line.split()
        if words[2] == "sda":
            break

    #print words[5], words[9]

    d["dr"] = long(words[5]) * 512
    d["dw"] = long(words[9]) * 512

    #
    #   get net statistics
    #

    fnet = open("/proc/net/dev")
    content = fnet.read()
    fnet.close()

    #print content

    receive = long(0)
    transmit = long(0)
    lines = content.splitlines()
    for line in lines:
        # ship non-interface lines
        if line.find(":") <= 0:
            continue

        line = line.replace(":"," ")
        words = line.split()

        # skip local interfaces
        if words[0] == "lo":
            continue
            
        #print "words", words
        #print words[1], words[9]
        receive += long(words[1])
        transmit += long(words[9])

    d["nr"] = receive
    d["nw"] = transmit

    return d

if __name__ == '__main__':

    if len(sys.argv) < 3: 
        print "Usage: " + sys.argv[0] + " <logdir> <logname>"
        sys.exit(1)
    
    logdir = sys.argv[1]
    logname = sys.argv[2]

    log = Logger(logdir,logname)

    d = {}
    it = -1

    # wait until a round second
    t = time.time()
    f = t - int(t)
    s = 1.0 - f
    #print s
    time.sleep(s)
    
    # get the first measurement
    t = time.time()
    d = getstat()
    it = int(t+0.5)

    # wait for the next round second
    t = time.time()
    f = t - int(t)
    s = 1.0 - f
    # if sleep terminates early, skip the remainder of the current second
    if s < 0.5:
        s += 1.0
    time.sleep(s)

    while 1:
        #r = resource.getrusage(resource.RUSAGE_SELF)
        #t0 = r.ru_utime + r.ru_stime
        #m0 = 1.0 * r.ru_maxrss / 1000

        # get the time and the counters
        t = time.time()

        dold = d
        d = getstat()

        itold = it
        it = int(t+0.5)
        #print "%.6f\t%d" % (t, it)

        # verify the jump correctness
        if (it - itold) < 1:
            print "*** Error: incorrect time jump", itold, it
            sys.stdout.flush()
            sys.exit(1)

        # get the counter offsets
        dnew = {}
        for key,value in d.iteritems():
            dnew[key] = value - dold[key]

        dstr = json.dumps(dnew)
        s = "%d\t%s" % (it, dstr)
        #print s

        log.write(it,dstr)
            
        #f = t - int(t)
        #s = 1.0 - f
        #print "%.6f\t%.6f\t%.6f\t%s" % (t, f, s, str(d))

        # wait for the next round second
        t = time.time()
        f = t - int(t)
        s = 1.0 - f
        # if sleep terminates early, skip the remainder of the current second
        if s < 0.5:
            s += 1.0
        #print s
        time.sleep(s)
        #t = time.time()
        #print "%.6f" % (t)

    log.close()

