import os
import sys
import time
import json
import threading
import urlparse
import logging
import subprocess
import shutil
import errno

import BaseHTTPServer
import SocketServer

"""
Assumptions:
    1 bil nodes
    
    32 machines
    32 cores each
    1024 workers in total

    => at least 1024 tasks
    => range at least 900,000
    => range for 100K => 23 MB, 200K => 54 MB
    => range for 900K => 200 MB

"""

USER = os.environ["USER"]

# workdir = os.environ["SNAPWEXEC"]
workdir = "/lfs/local/0/%s/fake_test/" % USER
python = "python"

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

class Server(BaseHTTPServer.BaseHTTPRequestHandler):

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
                
            start_time = time.time()

            dst = subpath[2]
            src = subpath[3]

            dirname = "snapw.%d/qin/%s" % (self.pid, dst)
            mkdir_p(dirname)

            self.server.glock.acquire()
            self.server.input_id += 1
            src = "TaskA-%d" % self.server.input_id
            self.server.glock.release()

            fname = "%s/%s" % (dirname, src)

            fd = os.open(fname, os.O_CREAT | os.O_EXCL | os.O_RDWR)
            f = os.fdopen(fd,"w")

            length = int(self.headers.get("Content-Length"))
            #print "Content-Length", length

            nleft = length
            while nleft > 0:
                nread = min(102400, nleft)
                body = self.rfile.read(nread)
                # f.write(body)
                nleft -= len(body)

            f.close()
    

            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()

            end_time = time.time()

            self.server.glock.acquire()
            self.server.input_count += 1
            self.server.consumed += length
            if self.server.start_time == 0 or start_time < self.server.start_time:
                self.server.start_time = start_time
            if self.server.end_time == 0 or end_time > self.server.end_time:
                self.server.end_time = end_time
            print "message: %s, length: %.2f MB" % (fname, length/float(1024*1024))
            throughput = (self.server.consumed/float(1024*1024)) / float(self.server.end_time - self.server.start_time)
            # print "latest", self.server.start_time, self.server.end_time, 
            print "Throughput: %.2f MB/s, Input Count: %d" % (throughput, self.server.input_count)
            self.server.glock.release()
            sys.stdout.flush()

            return

        return

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

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " -p <port>"
        sys.exit(1)

    
    host = "0.0.0.0"
    port = None
    master = None

    os.chdir(workdir)

    index = 1
    while index < len(sys.argv):
        arg = sys.argv[index]
        if arg == "-p":
            index += 1
            port = int(sys.argv[index])

        index += 1

    if port == None:
        print "Usage: %s -p <port>" % sys.argv[0]
        sys.exit(1)

    # Set up logging
    logging.basicConfig(filename="fake.log", level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')

    server = ThreadedHTTPServer((host, port), Server)
    server.host = host
    server.port = port
    server.running = True

    server.glock = threading.Lock()
    server.start_time = 0
    server.end_time = 0
    server.consumed = 0
    server.input_count = 0
    server.input_id = 0

    handler = BaseHTTPServer.BaseHTTPRequestHandler
    handler.port = port
    handler.id = id
    handler.pid = os.getpid()
    handler.workdir = workdir

    server.execute()

