#
#   Gatekeeper client library
#

import os
import random
import time
import httpclient
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] [%(levelname)s] [%(process)d] [%(filename)s] [%(funcName)s] %(message)s')

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

                logging.critical("*** Error *** acquire1")
                continue

            # return, if the result is OK
            if len(result) >= 2:
                if result[:2] == "OK":
                    break
                else:
                    logging.warn('tried to get token, response %s' % result)

            else:
                logging.critical("*** Error *** acquire2")
            # sleep 0.1-0.3s before repeating the request
            time.sleep(0.1 + random.random()/5.0)

        return result

    def release(self,ttype,tpid):
        """
        release a token
        """

        while 1:
            logging.debug('release token attempt')
            # send the request
            s = "/release/%s/%s" % (ttype,tpid)
            result = self.request(s,"")
            if result != None:
                logging.debug('release result not None!')
                break

            logging.critical("*** Error *** release1")
            # sleep 0.1-0.3s before repeating the request
            time.sleep(0.1 + random.random()/20.0)

        return result

