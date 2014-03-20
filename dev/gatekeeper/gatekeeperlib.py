#
#   Gatekeeper client library
#

import os
import random
import time
import httpclient

class GateKeeperClient(httpclient.HTTPClient):

    def acquire(self,ttype,tpid,tsize):
        """
        acquire a token
        """

        while 1:
            # send the request
            s = "/acquire/%s/%s/%d" % (ttype,tpid,tsize)
            result = self.request(s,"")
            if result == None:
                # sleep 0.1-0.3s before repeating the request
                time.sleep(0.1 + random.random()/20.0)

                print "*** Error *** acquire1", os.getpid()
                continue

            # return, if the result is OK
            if len(result) >= 2:
                status = False
                if result[:2] == "OK":
                    status = True
                break

            print "*** Error *** acquire2", os.getpid()
            # sleep 0.1-0.3s before repeating the request
            time.sleep(0.1 + random.random()/5.0)

        return status

    def release(self,ttype,tpid):
        """
        release a token
        """

        while 1:
            # send the request
            s = "/release/%s/%s" % (ttype,tpid)
            result = self.request(s,"")
            if result != None:
                break

            print "*** Error *** release1", os.getpid()
            # sleep 0.1-0.3s before repeating the request
            time.sleep(0.1 + random.random()/20.0)

        return result

