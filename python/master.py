import BaseHTTPServer
import SocketServer

import os
import sys
import urlparse
import json
import logging
import threading
import time

import client
import config
import perf

class Server(BaseHTTPServer.BaseHTTPRequestHandler):
    
    def do_GET(self):

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
                'server_type=%s' % "head server",
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

        command = parsed_path.path

        dargs = dict(urlparse.parse_qsl(parsed_path.query))

        if self.path == "/start":
            logging.info("starting host servers")

            self.timer.start("master")

            master = self.config["master"]
            hosts = self.config["hosts"]
            for h in hosts:
                self.StartHostServer(h, master)

        elif self.path == "/quit":
            self._quit()
            return

        elif self.path == "/dummy":
            logging.debug("dummy request")

            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()
            return

        elif self.path == "/config":
            logging.debug("get configuration")

            body = json.dumps(self.config)
            self.send_response(200)
            self.send_header('Content-Length', len(body))
            self.end_headers()
            self.wfile.write(body)
            return

        elif command == "/exec":
            pname = dargs.get("p")

            ptime = 0
            try:
                ptime = int(dargs.get("t"))
            except:
                pass
            # logging.debug("get executable: " + str(pname) + " " + str(ptime))

            stat = os.stat(pname)
            mtime = int(stat.st_mtime)

            swnew = False
            if mtime > ptime:
                swnew = True
            
            # logging.debug("stat " + str(pname) + " " + str(ptime) + " " + str(mtime) + " " + str("NEW" if swnew else "OLD"))
            if not swnew:
                # the file has not changed
                self.send_response(304)
                self.send_header('Content-Length', 0)
                self.end_headers()
                return

            f = open(pname)
            content = f.read()
            f.close()

            self.send_response(200)
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
            return

        elif subpath[1] == "done":
            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()

            if len(subpath) > 2:
                host = subpath[2]
                
                self.server.done_lock.acquire()
                self.server.done.add(host)
                logging.info("host %s completed work" % (str(self.server.done)))
                done_size = len(self.server.done)
                self.server.done_lock.release()

                if done_size == len(self.config["hosts"]):

                    logging.info("all hosts completed")
                    # Fix possible concurrency issue with supervisor.py
                    time.sleep(5)

                    # initialize a set of ready servers,
                    # clear the continue indicator
                    self.server.ready_lock.acquire()
                    self.server.ready = set()
                    self.server.ready_lock.release()

                    self.server.iterate = False

                    # send a start message at the beginning
                    if not self.server.start:
                        self.server.start = True
                        self.server.executing = True
                        (starthost, starttask) = self.GetStartInfo(self.config)
                        s = "send __Start__ message for task %s to host %s" % (
                                starttask, starthost)
                        logging.debug(s)
                        client.message(starthost,"__Main__",starttask,"__Start__")

                    # send a step start command to all the hosts
                    hosts = self.config["hosts"]
                    master = "%s:%s" % (
                        self.config["master"]["host"],
                        self.config["master"]["port"])

                    logging.debug("hosts " + str(hosts))
                    for h in hosts:
                        logging.debug("send prepare to " + str(h))
                        self.Prepare(h)
                        logging.debug("done sending prepare to " + str(h))
            return

        elif subpath[1] == "ready":
            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()

            if len(subpath) > 2:
                host = subpath[2]

                if self.timer.has_tag("ready-%s" % host):
                    self.timer.stop("ready-%s" % host)
                    cmd = "./snapshot.sh %d" % self.snapshot_counter
                    self.snapshot_counter += 1
                    logging.info(cmd)
                    os.system(cmd)

                self.timer.start("ready-%s" % host)

                # get the number of active tasks on the host
                numtasks = 0
                try:
                    numtasks = int(subpath[3])
                except:
                    pass

                # execute the next step, if there are active tasks
                if numtasks > 0:
                    self.server.iterate = True

                self.server.ready_lock.acquire()
                self.server.ready.add(host)
                logging.debug("host %s ready" % (str(self.server.ready)))
                ready_size = len(self.server.ready)
                self.server.ready_lock.release()

                if ready_size == len(self.config["hosts"]):

                    # stop the execution, if there are no more tasks to execute
                    if not self.server.iterate:
                        logging.info("all tasks completed")
                        self.server.executing = False
                        self.server.iterate = False
                        self._quit(force=True)
                        return

                    logging.info("all hosts ready")
        
                    # initialize a set of done servers
                    self.server.done_lock.acquire()
                    self.server.done = set()
                    self.server.done_lock.release()

                    # send a step start command to all the hosts
                    hosts = self.config["hosts"]
                    master = "%s:%s" % (
                        self.config["master"]["host"],
                        self.config["master"]["port"])

                    # TODO: create a thread for this step
                    for h in hosts:
                        logging.info("send next step to " + str(h))
                        self.StartStep(h)
            return

        elif subpath[1] == "error":

            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()

            if len(subpath) > 3:
                src_host = subpath[2]
                encoded_msg = subpath[3]
                msg_dict = urlparse.parse_qs(encoded_msg)
                logging.critical("Error msg from supervisor %s: %s" % (src_host, msg_dict['msg']))
                logging.critical("Terminating master now")
                self._quit(force=True)

            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(message)
        return

    def _quit(self, force=False):
        logging.info("terminating host servers")

        # master = self.config["master"]
        hosts = self.config["hosts"]
        for h in hosts:
            self.QuitHostServer(h)

        if not force:
            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()

        # set the flag to terminate the server
        self.server.running = False
        self.server.self_dummy()

        if self.timer.has_tag("master"):
            self.timer.stop("master")

    def StartHostServer(self, remote, master):
        logging.info("starting host server on host %s, port %s" % \
                (remote["host"], remote["port"]))

        #cmd = "ssh %s python git/rok/snapworld/host.py -i %s -p %s -m %s:%s" % (
        #cmd = "ssh %s python git/rok/snapworld/host.py -d -i %s -p %s -m %s:%s" % (
        #cmd = "ssh %s python2.6 /lfs/1/tmp/rok/snapworld/host.py -d -i %s -p %s -m %s:%s" % (

        init_script = self.config.get('init', 'supervisor.sh')
        cmd = "ssh %s %s %s %s %s %s" % (
                    remote["host"], init_script, remote["id"], remote["port"],
                    master["host"], master["port"])
        logging.info(cmd)
        os.system(cmd)

    def GetStartInfo(self, config):
        starttask = "%s-0" % (config["route"]["1"]["__Start__"])
        starthost = config["tasks"][starttask]

        hosts = config["hosts"]
        for host in hosts:
            if host["id"] == starthost:
                result = "%s:%s" % (host["host"], host["port"])
                return result, starttask

        return None

    def StartStep(self, host):
        haddr = "%s:%s" % (host["host"], host["port"])
        client.step(haddr)

    def Prepare(self, host):
        haddr = "%s:%s" % (host["host"], host["port"])
        client.prepare(haddr)

    def QuitHostServer(self, host):
        haddr = "%s:%s" % (host["host"], host["port"])
        client.quit(haddr)

    def log_request(self, code=None, size=None):
        pass

    def log_message(self, format, *args):
        pass

class ThreadedHTTPServer(SocketServer.ThreadingMixIn,
                            BaseHTTPServer.HTTPServer):
    """Handle requests in a separate thread."""

    def execute(self):
        while self.running:
            self.handle_request()

        logging.debug("exit")
        sys.exit(0)

    def self_dummy(self):
        haddr = "%s:%s" % (self.host, self.port)
        client.dummy(haddr)


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] [%(asctime)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')

    dconf = config.readconfig("snapw.config")
    logging.info(str(dconf))

    master = dconf["master"]

    host = master["host"]
    port = int(master["port"])

    server = ThreadedHTTPServer((host, port), Server)
    # head service host name
    server.host = host
    # head service port
    server.port = port
    # set of hosts completed their step
    server.done = set()
    server.done_lock = threading.Lock()
    # set of hosts ready for the next step
    server.ready = set()
    server.ready_lock = threading.Lock()
    # indicator, if an application has started yet
    server.start = False
    # indicator that the head service is running
    server.running = True
    # indicator that an application is running
    server.executing = False
    # indicator that an application should execute the next step
    server.iterate = False

    handler = BaseHTTPServer.BaseHTTPRequestHandler
    handler.config = dconf
    handler.timer = perf.Timer(logging)
    handler.snapshot_counter = 0

    dconf["tasks"] = config.assign(dconf)

    logging.info('Starting head server on port %d, use <Ctrl-C> to stop' % (port))
    server.execute()

