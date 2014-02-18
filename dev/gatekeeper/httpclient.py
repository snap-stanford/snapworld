#!/usr/bin/env python

#
#	HTTP service client
#

import httplib
import random
import os
import struct
import socket
import time

class HTTPClient:

    def __init__(self,host,port):
        self.host = host
        self.port = port

        # set the default socket timeout to 10s
        socket.setdefaulttimeout(10)

        self.open()

    def close(self):
        self.h.sock.shutdown(socket.SHUT_RDWR)
        l_onoff, l_linger = 1, 0 # send RST (hard reset the socket) right away
        self.h.sock.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                        struct.pack('ii', l_onoff, l_linger))
        self.h.close()

    def request(self,params,body):
        """
        execute a request
        """

        count = 0
        while 1:
            try:
                #if 'TCP_QUICKACK' in socket.__dict__:
                #    self.h.sock.setsockopt(socket.SOL_TCP, socket.TCP_QUICKACK, 1)
                result = self.handle_request(params,body)
                return result
            except:
                self.close()

            count += 1
            print "*** Error *** request1", os.getpid(), count
            # sleep from 0.0-0.2s
            time.sleep(random.random()/5.0)
            self.open()

    def open(self):
        """
        open a connection to the server
        """

        count = 0
        while 1:
            try:
                self.h = httplib.HTTPConnection(self.host,self.port)
                self.h.connect()
                #if 'SO_REUSEADDR' in socket.__dict__:
                #    self.h.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                if 'TCP_NODELAY' in socket.__dict__:
                    self.h.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

                break
            except:
                pass

            count += 1
            print "*** Error *** open1", os.getpid(), count
            # sleep from 1.0-1.5s
            time.sleep(1.0+random.random())

    def handle_request(self,params,body):

        req = self.h.request("GET",params,body)

        if 'TCP_QUICKACK' in socket.__dict__:
            self.h.sock.setsockopt(socket.SOL_TCP, socket.TCP_QUICKACK, 1)
        if 'TCP_NODELAY' in socket.__dict__:
            self.h.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)

        resp = self.h.getresponse()

        if resp == None:
            return None
        if resp.getheader("Content-Length") == None:
            return None

        result = resp.read()

        if resp.status != 200:
            return None

        return result

