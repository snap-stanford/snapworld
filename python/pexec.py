#! /usr/bin/python

import subprocess

#python /home/rok/git/rok/snapworld/GenTasks.py -t GenTasks-0 -h localhost:9100 -q /home/rok/snapwexec/snapw.2687/qact/GenTasks-0

def Exec(pwd, cmd):

    # split into individual arguments, since we are not using shell
    cl = cmd.split()
    cmd_ref = cmd
    # start the process
    #p = subprocess.Popen(cl, cwd=pwd, stderr=subprocess.STDOUT, stdout=1)
    #p = subprocess.Popen(cl, cwd=pwd, stdout=1)
    p = subprocess.Popen(cl, cwd=pwd)
    return p

def GetPid(p):
	return p.pid

def Poll(p):
    status = p.poll()
    return status

