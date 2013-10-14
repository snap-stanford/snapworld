import os
import sys
import time
import shlex
import subprocess

def get_system_stats():
    d = {}

    #  Get CPU statistics

    fcpu = open("/proc/stat")
    content = fcpu.read()
    fcpu.close()

    lines = content.splitlines()
    for line in lines:
        words = line.split()
        if words[0] == "cpu":
            break

    d["cpu_user"] = long(words[1]) + long(words[2])
    d["cpu_user"] = long(words[1]) + long(words[2])
    d["cpu_system"] = long(words[3])
    d["cpu_idle"] = long(words[4])
    d["cpu_wait"] = long(words[5])
    d["cpu_inter"] = long(words[6]) + long(words[7])

    # Get Disk statistics

    fdisk = open("/proc/diskstats")
    content = fdisk.read()
    fdisk.close()

    lines = content.splitlines()
    for line in lines:
        words = line.split()
        if words[2] == "sda":
            break

    d["disk_read"] = long(words[5]) * 512
    d["disk_write"] = long(words[9]) * 512

    # Get Network statistics

    fnet = open("/proc/net/dev")
    content = fnet.read()
    fnet.close()

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
            
        receive += long(words[1])
        transmit += long(words[9])

    d["net_receive"] = receive
    d["net_transmit"] = transmit

    return d

if __name__ == '__main__':
    d = get_system_stats()
    if len(sys.argv) > 1 and sys.argv[1] == "--file":
        for k, v in d.items():
            print k, v
    else:
        print d

