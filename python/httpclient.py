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
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')

class HTTPClient:

    def __init__(self,host,port):
        self.host = host
        self.port = int(port)

        # set the default socket timeout to 10s
        #socket.setdefaulttimeout(10)

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
            logging.critical("*** Error *** request1, count %d" % count)
            # sleep from 0.0-0.2s
            time.sleep(random.random()/5.0)
            self.open()

    def open(self):
        """
        open a connection to the server
        """

        count = 0
        while 1:
            logging.debug('open attempt number %d for host %s on port %d' % (count,self.host,self.port))
            try:
                self.h = httplib.HTTPConnection(self.host,self.port)
                self.h.connect()
                if 'TCP_NODELAY' in socket.__dict__:
                    self.h.sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
                if self.h.sock is None:
                    logging.critical("how could this happen? nonetype socket object?")
                    raise Exception("gah!")

                break
            except:
                pass

            count += 1
            logging.warn("*** Error *** open1 %d %d" % (os.getpid(), count))
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

