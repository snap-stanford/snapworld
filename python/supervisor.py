import os
import sys
import time
import json
import threading
import urlparse
import logging
import subprocess
import shutil

import BaseHTTPServer
import SocketServer

import client
import config
import daemon
import perf

bindir = os.environ["SNAPWBIN"]
workdir = os.environ["SNAPWEXEC"]
python = os.environ["PYTHON"]

sys.path.append(bindir)


class Server(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):
        #print "GET path", self.path
        parsed_path = urlparse.urlparse(self.path)
        message_parts = [
                'CLIENT VALUES:',
                'client_address=%s (%s)' % (self.client_address,
                                            self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'real path=%s' % parsed_path.path,
                'query=%s' % parsed_path.query,
                'request_version=%s' % self.request_version,
                '',
                'SERVER VALUES:',
                'server_type=%s' % "host server",
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                '',
                'HEADERS RECEIVED:',
                ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')
        message = '\r\n'.join(message_parts)

        subpath = self.path.split("/")

        if self.path == "/prepare":

            # move qin to qact
            qinname = "snapw.%d/qin" % (self.pid)
            qactname = "snapw.%d/qact" % (self.pid)

            # rename an existing qact
            if os.path.exists(qactname):

                removed = False
                if not self.config['debug']:
                    try:
                        shutil.rmtree(qactname)
                        logging.debug("removed dir %s" % qactname)
                        removed = True
                    except:
                        logging.error("error on removing dir %s" % qactname)

                if not removed:
                    t = time.time()
                    s = time.strftime("%Y%m%d-%H%M%S", time.localtime(t))
                    mus = "%06d" % (t*1000000 - int(t)*1000000)
                    qactnewname = "%s-%s-%s" % (qactname, s, mus)
                    os.rename(qactname, qactnewname)
                    logging.debug("renamed %s to %s" % (qactname, qactnewname))
                    
            # get the number of active tasks, rename existing qin
            numtasks = 0
            if os.path.exists(qinname):
                os.rename(qinname, qactname)
                active = os.listdir(qactname)
                numtasks = len(active)

            # create new qin
            config.mkdir_p(qinname)
    
            logging.info("preparing next step: %s, %s" % \
                    (qinname, qactname))

            # send ready to master
            client.ready(self.master, self.id, numtasks)

            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()
            return

        elif self.path == "/quit":
            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()

            # set the flag to terminate the server
            self.server.running = False
            self.server.self_dummy()
            return

        elif self.path == "/dummy":
            logging.debug("dummy request")

            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()
            return

        elif self.path == "/step":
    
            logging.info("execute next step")

            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()

            # TODO, implement null action,
            #   skip execution if there are no tasks to execute,
            #   qact does not exist

            # get the tasks to execute
            qactname = "snapw.%d/qact" % (self.pid)
            active = []
            if os.path.exists(qactname):
                active = os.listdir(qactname)

            logging.debug("active tasks %s" % (str(active)))

            self.qactname = qactname
            self.active = active # the task list
            # start a thread to execute the work tasks
            t = threading.Thread(target=Execute, args=(self, ))
            t.start()
            return

        elif self.path == "/config":
    
            logging.debug("get configuration")

            body = json.dumps(self.config)
            self.send_response(200)
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)

            return

        elif self.path == "/quit":
    
            logging.info("terminate execution")

            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()
            sys.exit(0)

        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return

    def do_POST(self):
        #print "POST path", self.path
        parsed_path = urlparse.urlparse(self.path)
        message_parts = [
                'CLIENT VALUES:',
                'client_address=%s (%s)' % (self.client_address,
                                            self.address_string()),
                'command=%s' % self.command,
                'path=%s' % self.path,
                'real path=%s' % parsed_path.path,
                'query=%s' % parsed_path.query,
                'request_version=%s' % self.request_version,
                '',
                'SERVER VALUES:',
                'server_type=%s' % "host server",
                'server_version=%s' % self.server_version,
                'sys_version=%s' % self.sys_version,
                'protocol_version=%s' % self.protocol_version,
                '',
                'HEADERS RECEIVED:',
                ]
        for name, value in sorted(self.headers.items()):
            message_parts.append('%s=%s' % (name, value.rstrip()))
        message_parts.append('')
        message = '\r\n'.join(message_parts)

        length = int(self.headers.get("Content-Length"))

        body = ""
        subpath = self.path.split("/")
        
        if subpath[1] == "msg":
            dst = subpath[2]
            src = subpath[3]

            dirname = "snapw.%d/qin/%s" % (self.pid, dst)
            config.mkdir_p(dirname)

            fname = "%s/%s" % (dirname, src)
            f, fnew = config.uniquefile(fname)
            if fname <> fnew:
                logging.warn("uniquefile?: %s; %s; %s; %s;" % (dirname, src, fname, fnew))

            length = int(self.headers.get("Content-Length"))
            #print "Content-Length", length

            try:
                nleft = length
                while nleft > 0:
                    nread = min(102400, nleft)
                    body = self.rfile.read(nread)
                    f.write(body)
                    nleft -= len(body)
            except Exception as e:
                logging.warn("file stream error: %s" % str(e))
                try:
                    f.close()
                    os.remove(fnew)
                except:
                    pass
                try:
                    self.send_response(200)
                    self.send_header('Content-Length', 0)
                    self.end_headers()
                except:
                    pass
                return
                
            f.close()
            logging.info("message %s length %d" % (fnew,  length))

            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()
            return

        length = int(self.headers.get("Content-Length"))
        #print "Content-Length", length

        body = ""
        if length  and  length > 0:
            body = self.rfile.read(length)

        # Begin the response
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Client: %s\n' % str(self.client_address))
        self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
        self.wfile.write('Path: %s\n' % self.path)

    def log_message(self, format, *args):
        pass

class ThreadedHTTPServer(SocketServer.ThreadingMixIn,
                            BaseHTTPServer.HTTPServer):
    """Handle requests in a separate thread."""

    def execute(self):
        while self.running:
            self.handle_request()

        # For *-py-*.log
        logging.info("Exit")
        # For *-sh-*.log
        # print "Exit"
        sys.stdout.flush()
        sys.exit(0)

    def self_dummy(self):
        haddr = "%s:%s" % (self.host, self.port)
        client.dummy(haddr)

def get_task_name(task):
    return str(task.split('-', 1)[0])

def Execute(args):
    logging.info("Execute " + str(args.active) + "")
    tnow = time.time()
    overall_timer = perf.Timer(logging)
    task_name = "overall: "
    if len(args.active) > 0:
        # Get's the task name
        task_name = "overall: %s" % get_task_name(args.active[0])
    overall_timer.start(task_name)

    if len(args.active) > 0:
        execdir = os.path.join(args.workdir, "snapw.%d/exec" % (args.pid))
        config.mkdir_p(execdir)
     
    def execute_single_task(task):
        # get the executables
        bunch = get_task_name(task)
        execlist = []
        try:
            execlist = args.config["bunch"][bunch]["exec"].split(",")
        except:
            pass
     

        timer = perf.Timer(logging)
        timer.start('provision-execlist')
        # provision execlist on disk
        for item in execlist:
            execpath = os.path.join(execdir, item)
            # check if the program exists and its mtime
            mtime = None
            try:
                stat = os.stat(execpath)
                mtime = int(stat.st_mtime)
            except:
                pass
     
            if not mtime or mtime < tnow:
                # if the file does not exist or it is older than current time,
                # contact the head task
     
                content = client.getexec(args.master,item,mtime)
                swc = "None"
                if content:
                    swc = str(len(content))
     
                logging.debug("Host received %s" % (swc))
                if content:
                    if len(content) > 0:
                        logging.debug("Host saving to %s" % (execpath))
                        f = open(execpath,"w")
                        f.write(content)
                        f.close()
       
                    os.utime(execpath,(tnow, tnow))
        timer.stop('provision-execlist')
     
        prog = execlist[0]
        logging.debug("Task %s, exec %s" % (prog, execlist))
        progpath = os.path.join(execdir, prog)
     
        if not os.path.exists(progpath):
            logging.error("task %s not started, program %s not found" % (task, progpath))
            return
     
        taskdir = "snapw.%d/tasks/%s" % (args.pid, task)
        config.mkdir_p(taskdir)
     
        qdir = os.path.join(args.workdir, args.qactname, task)
        tdir = os.path.join(args.workdir, taskdir)
     
        logging.info("starting task %s, prog %s, workdir %s, qdir %s\n" % (task, prog, tdir, qdir))
             
        # get server information
        host = args.server.host
        port = args.server.port
     
        # construct a command line
        cmd = python + " %s -t %s -h %s:%d -q %s" % (
            progpath, task, host, port, qdir)
        logging.info("starting cmd %s" % (cmd))
     
        # start the work process
        p = subprocess.Popen(cmd.split(), cwd=tdir, close_fds=True)
        return p, prog
     
    # Dynamically check what the number of processors we have on each host
    # In any error, default to 1.
    max_tasks = 1
    var_par_tasks = int(args.config['par_tasks'])
    if var_par_tasks <= 0:
        try:
            max_tasks = os.sysconf('SC_NPROCESSORS_ONLN')
        except:
            max_tasks = 1
    else:
        max_tasks = var_par_tasks

    # execute the tasks in a parallel fashion by running
    # at most max_tasks processes at any point.
    task_list = args.active[:]
    procs = []
    logging.info("Running %d tasks with %d-way parallelism: %s" % \
            (len(task_list), max_tasks, str(task_list)))

    timer = perf.Timer(logging)
    pcounter = 0
    counter_map = {}
    while True:
        while task_list and len(procs) < max_tasks:
            task = task_list.pop()
            timer.start("prog-%d" % pcounter)
            p, prog = execute_single_task(task)
            timer.update_extra("prog-%d" % pcounter, "%d, %s" % (p.pid, prog))
            counter_map[p.pid] = pcounter
            pcounter += 1
            procs.append(p)

        for p in procs:
            # wait for the process to complete
            
            pid = p.pid
            logging.debug("polling %d" % pid)
            status = p.poll()
            if status is not None:
                timer.stop("prog-%d" % counter_map[p.pid])
                del counter_map[p.pid]

                logging.debug("finished %d with status %s" % (pid, str(status)))
                # error reporting
                if status <> 0:
                    msg = "Pid %d terminated unexpectedly with status %d" % (pid, status)
                    logging.error(msg)
                    client.error(args.master, args.id, msg)

                procs.remove(p) 
 
        if not procs and not task_list:
            break
        else:
            time.sleep(1.0)

    overall_timer.stop(task_name)
    # send done to master
    client.done(args.master, args.id)

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " -d -i <id> -p <port> -m <host>:<port>"
        sys.exit(1)

    
    host = "0.0.0.0"
    port = None
    master = None

    daemon_mode = False
    index = 1
    while index < len(sys.argv):
        arg = sys.argv[index]
        if arg == "-i":
            index += 1
            id = sys.argv[index]
        elif arg == "-p":
            index += 1
            port = int(sys.argv[index])
        elif arg == "-m":
            index += 1
            master = sys.argv[index]
        elif arg == "-d":
            daemon_mode = True

        index += 1

    if port == None:
        print "Usage: %s -d -i <id> -p <port> -m <host>:<port>" % sys.argv[0]
        sys.exit(1)

    if daemon_mode:
        # TODO: How to log this? Do we need to log this?
        # print "Daemonizing..."
        # sys.stdout.flush()
        retCode = daemon.createDaemon()

    # print "Starting Supervisor..."
    # sys.stdout.flush()

    # NOTE: Cannot do sys.stdout.flush()
    # Will have funny behavior...

    os.chdir(workdir)
    pid = os.getpid()

    fname = "supervisor-py-%d.log" % pid

    ### Daemon Stuff
    fname1 = "supervisor-sh-%d.log" % port
    fd = os.open(fname1, os.O_APPEND | os.O_WRONLY) # standard input (0)
    # Duplicate standard input to standard output and standard error.
    os.dup2(0, 1)           # standard output (1)
    os.dup2(0, 2)           # standard error (2)
    ###

    # Set up logging
    logging.basicConfig(filename=fname, level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')

    server = ThreadedHTTPServer((host, port), Server)
    server.host = host
    server.port = port
    server.running = True

    handler = BaseHTTPServer.BaseHTTPRequestHandler
    handler.port = port
    handler.id = id
    handler.pid = os.getpid()
    handler.workdir = workdir
    handler.master = master

    if master != None:
        # get configuration from master
        sconf = client.config(master)
    
        dconf = json.loads(sconf)
        handler.config = dconf
    
        logging.debug("Config size: %d" % (len(sconf)))
        logging.debug(str(dconf))
            
        # send done to master
        client.done(master, id)

        # NOTE: Time conflict. The master might already send 'step' request,
        #       before server_forever() is started, so 'step' might be lost.
        #       Delay done until the server is up and running.
        # Check out Asynchronous Mixins example for SocketServer
        # Comment: the constructor might already activate the server,
        #       so there is no problem.
        # NOTE: Fixed using time.sleep(5) in master.py

        logging.debug("Supervisor sent /done to master")

    logging.info("Starting host server pid %d, id %s, port %d with master %s\n" % (pid, id, port, master))
    
    server.execute()

