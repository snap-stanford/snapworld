#!/usr/bin/python

import BaseHTTPServer
import SocketServer

import os
import simplejson
import sys
import time
import urlparse
import urllib2

import config
import daemon

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

        #if self.path == "/start":
        #    print "starting"

        self.send_response(200)
        #self.send_header('Last-Modified', self.date_time_string(time.time()))
        self.end_headers()
        self.wfile.write(message)
        return

    def do_POST(self):
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
        print "Usage: " + sys.argv[0] + " -i <id> -p <port> -m <host>:<port>"
        sys.exit(1)

    port = None
    master = None

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

        index += 1

    if port == None  or  master == None:
        print "Usage: " + sys.argv[0] + " -i <id> -p <port> -m <host>:<port>"
        sys.exit(1)

    retCode = daemon.createDaemon()

    os.chdir("/home/rok/snapwexec")

    pid = os.getpid()
    fname = "log-swhost-%d.txt" % (pid)
    flog = open(fname,"w")

    server = ThreadedHTTPServer(('localhost', port), Server)

    handler = BaseHTTPServer.BaseHTTPRequestHandler
    handler.flog = flog

    # get configuration from master
    url = "http://%s/config" % (master)
    f = urllib2.urlopen(url)
    sconf = f.read()
    f.close()

    dconf = simplejson.loads(sconf)
    handler.dconf = dconf

    flog.write("Got configuration size %d\n" % (len(sconf)))
    flog.write(str(dconf))
    flog.write("\n")

    # send done to master
    url = "http://%s/done/%s" % (master,id)
    f = urllib2.urlopen(url)
    sconf = f.read()
    f.close()

    pid = os.getpid()
    flog.write(
        "Starting host server pid %d, id %s, port %d with master %s\n" %
            (pid, id, port, master))
    flog.flush()

    server.serve_forever()

