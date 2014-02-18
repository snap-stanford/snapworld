import os
import sys
import time
import thread
import urlparse
import logging

import BaseHTTPServer
import SimpleHTTPServer
import SocketServer

sys.path.append("../python")
sys.path.append("../../python")

import daemon

try:
    bindir = os.environ["SNAPW_BIN"]
except:
    bindir = "."
try:
    workdir = os.environ["SNAPW_EXEC"]
except:
    workdir = "."

TMAX = 3

sys.path.append(bindir)

class HTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        #logging.info("GET path %s" % self.path)
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
        #logging.info("request .%s." % str(subpath))

        if subpath[1] == "acquire":

            # get the token type and the max of tokens
            ttype = subpath[2]
            tpid = subpath[3]
            tsize = int(subpath[4])

            self.lock.acquire(True)

            result = "notOK"
            s = self.dtoken.get(ttype)
            if not s:
                # create the set, this is the first element
                s = set()
                s.add(tpid)
                self.dtoken[ttype] = s
                result = "OK"
            elif len(s) < TMAX:
                # a token is available
                s.add(tpid)
                result = "OK"
                #logging.info("acquire-1 %d %s %s" % (len(s), tpid, result))

            self.lock.release()

            self.send_response(200)
            self.send_header('Content-Length', len(result))
            self.end_headers()
            self.wfile.write(result)

            logging.info("acquire %d %s %s" % (len(s), tpid, result))
            return

        elif subpath[1] == "release":

            # get the token type and the max of tokens
            ttype = subpath[2]
            tpid = subpath[3]

            self.lock.acquire(True)
            s = self.dtoken.get(ttype)
            if s:
                s.discard(tpid)
            self.lock.release()

            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()

            logging.info("release %d %s" % (len(s), tpid))
            return

        # this call terminates the process
        elif subpath[1] == "quit":
    
            logging.info("terminate execution")
            self.send_response(200)
            self.send_header('Content-Length', 0)
            self.end_headers()

            # set the flag to terminate the server
            self.server.running = False

            return

        # return a request, if there is no match
        #   useful for debugging
        self.send_response(200)
        self.send_header('Content-Length', 0)
        self.end_headers()
        return

    def do_POST(self):
        #logging.info("POST path %s" % self.path)
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
        
        # TODO change to match another API request
        if subpath[1] == "msg":
            dst = subpath[2]
            src = subpath[3]

            # TODO, do the work here

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

class HTTPServer (BaseHTTPServer.HTTPServer):

    def serve_forever(self):

        self.running = True
        while self.running:
            self.handle_request()

        # For *-py-*.log
        logging.info("exiting")
        # For *-sh-*.log
        # print "Exit"
        sys.stdout.flush()
        sys.exit(0)

class ThreadedHTTPServer(SocketServer.ThreadingMixIn, HTTPServer):
    pass

def execute(host, port):

    iport = int(port)
    server_address = ('', iport)

    handler = HTTPRequestHandler
    handler.protocol_version = 'HTTP/1.1'
    handler.lock = thread.allocate_lock()
    handler.dtoken = {}

    server = ThreadedHTTPServer
    #server.daemon_threads = True

    httpd = server(server_address, handler)
    httpd.serve_forever()

usage = "Usage: %s -d -p <port>"

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print usage % sys.argv[0]
        sys.exit(1)

    host = "0.0.0.0"
    port = None

    daemon_mode = False
    index = 1
    while index < len(sys.argv):
        arg = sys.argv[index]
        if arg == "-p":
            index += 1
            port = int(sys.argv[index])
        elif arg == "-d":
            daemon_mode = True

        index += 1

    if port == None:
        print usage % sys.argv[0]
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

    #fname = "log-gatekeeper-%d.txt" % pid
    fname = "log-gatekeeper.txt"

    ### Daemon Stuff
    if daemon_mode:
        fname1 = "log-gatekeeper-%d.txt" % port
        fd = os.open(fname1, os.O_CREAT | os.O_APPEND | os.O_WRONLY) # standard input (0)
        # Duplicate standard input to standard output and standard error.
        os.dup2(0, 1)           # standard output (1)
        os.dup2(0, 2)           # standard error (2)

    # Set up logging
    logging.basicConfig(filename=fname, level=logging.DEBUG, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')

    logging.info("Starting host server pid %d, port %d" % (pid, port))
    execute(host, port)

