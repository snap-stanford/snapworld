#!/usr/bin/python

import BaseHTTPServer
import SocketServer

import os
import simplejson
import sys
import time
import urlparse
import urllib2

sys.path.append("/home/rok/git/rok/snapworld")

import client
import config
import daemon

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

        #print message
        #self.flog.write(message)
        #self.flog.flush()

        subpath = self.path.split("/")
        #print subpath

        if self.path == "/prepare":

            # move qin to qact

            qinname = "snapw.%d/qin" % (self.pid)
            qactname = "snapw.%d/qact" % (self.pid)

            # rename an existing qact
            qactnewname = "none"
            if os.path.exists(qactname):
                t = time.time()
                s = time.strftime("%Y%m%d-%H%M%S", time.localtime(t))
                mus = "%06d" % (t*1000000 - int(t)*1000000)
                qactnewname = "%s-%s" % (s, mus)
                os.rename(qactname, qactnewname)

            os.rename(qinname, qactname)

            # create new qin
            config.mkdir_p(qinname)

            # send ready to master
            client.ready(master, self.id)
    
            line = "preparing next step: %s, %s, %s\n" % (
                        qinname, qactname, qactnewname)
            flog.write(line)
            flog.flush()

        elif self.path == "/step":
    
            line = "execute next step\n"
            flog.write(line)
            flog.flush()

            # get the tasks to execute

            qactname = "snapw.%d/qact" % (self.pid)
            active = os.listdir(qactname)
    
            line = "active tasks %s\n" % (str(active))
            flog.write(line)
            flog.flush()

            for task in active:
                prog = "%s.py" % (task.split("-",1)[0])
    
                line = "starting task: %s %s\n" % (task, prog)
                flog.write(line)
                flog.flush()

                # TODO !!! execute the local task

        self.send_response(200)
        #self.send_header('Last-Modified', self.date_time_string(time.time()))
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
        #print message

        length = int(self.headers.get("Content-Length"))
        #print "Content-Length", length

        body = ""
        if length  and  length > 0:
            body = self.rfile.read(length)

        #print "length", length
        #print "body"
        #print body

        subpath = self.path.split("/")
        #print subpath
        
        if subpath[1] == "msg":
            dst = subpath[2]
            src = subpath[3]
            #print "msg", dst, src
            #print "body", body

            dirname = "snapw.%d/qin/%s" % (self.pid, dst)
            config.mkdir_p(dirname)

            fname = "%s/%s" % (dirname, src)
            f,fnew = config.uniquefile(fname)
            f.write(body)
            f.close()
    
            line = "message %s length %d\n" % (fnew,  length)
            flog.write(line)
            flog.flush()

        # Begin the response
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Client: %s\n' % str(self.client_address))
        self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
        self.wfile.write('Path: %s\n' % self.path)

    def do_POST1(self):
        # Parse the form data posted
        form = cgi.FieldStorage(
            fp=self.rfile, 
            headers=self.headers,
            environ={'REQUEST_METHOD':'POST',
                     'CONTENT_TYPE':self.headers['Content-Type'],
                     })

        # Begin the response
        self.send_response(200)
        self.end_headers()
        self.wfile.write('Client: %s\n' % str(self.client_address))
        self.wfile.write('User-agent: %s\n' % str(self.headers['user-agent']))
        self.wfile.write('Path: %s\n' % self.path)
        self.wfile.write('Form data:\n')

        # Echo back information about what was posted in the form
        for field in form.keys():
            field_item = form[field]
            if field_item.filename:
                # The field contains an uploaded file
                file_data = field_item.file.read()
                file_len = len(file_data)
                del file_data
                self.wfile.write('\tUploaded %s as "%s" (%d bytes)\n' % \
                        (field, field_item.filename, file_len))
            else:
                # Regular form value
                self.wfile.write('\t%s=%s\n' % (field, form[field].value))
        return

class ThreadedHTTPServer(SocketServer.ThreadingMixIn,
                            BaseHTTPServer.HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print "Usage: " + sys.argv[0] + " -d -i <id> -p <port> -m <host>:<port>"
        sys.exit(1)

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
        print "Usage: " + sys.argv[0] + " -d -i <id> -p <port> -m <host>:<port>"
        sys.exit(1)

    if daemon_mode:
        retCode = daemon.createDaemon()

    os.chdir("/home/rok/snapwexec")

    pid = os.getpid()
    #print "pid", pid

    fname = "log-swhost-%d.txt" % (pid)
    flog = open(fname,"w")

    server = ThreadedHTTPServer(('localhost', port), Server)

    handler = BaseHTTPServer.BaseHTTPRequestHandler
    handler.flog = flog
    handler.id = id
    handler.pid = os.getpid()

    if master != None:
        # get configuration from master
        sconf = client.config(master)
    
        dconf = simplejson.loads(sconf)
        handler.dconf = dconf
    
        flog.write("Got configuration size %d\n" % (len(sconf)))
        flog.write(str(dconf))
        flog.write("\n")
        flog.flush()
    
        # send done to master
        client.done(master, id)

        # TODO time conflict. The master might already send 'step' request,
        #       before server_forever() is started, so 'step' might be lost.
        #       Delay done until the server is up and running.
        # check out Asynchronous Mixins example for SocketServer
        # Comment: the constructor might already activate the server,
        #       so there is no problem.
    
        flog.write("Sent done\n")
        flog.flush()

    flog.write(
        "Starting host server pid %d, id %s, port %d with master %s\n" %
            (pid, id, port, master))
    flog.flush()

    server.serve_forever()

