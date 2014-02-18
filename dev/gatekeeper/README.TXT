Testing gatekeeper server and client
Feb 17, 2014

Starting the gatekeeper service from a command line:
  python gatekeeper.py -p <port>

Starting the gatekeeper service from a command line as a daemon:
  python gatekeeper.py -d -p <port>

An example of starting the service:
  python gatekeeper.py -p 1234

An example of starting a single client test:
  time python gktest.py

An example of starting 32 concurrent client tests:
  time python runProc4.py gktest.sh 32

