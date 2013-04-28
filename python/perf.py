import time

class Timer(object):
    def __init__(self, log, tag=None):
        self.log = log
        self.tag = tag

    def start(self, tag=None):
        if tag is not None:
            self.tag = tag
        self._start_time = time.time()

    def stop(self):
        time_taken = time.time() - self._start_time
        self.log.debug("[timer] [%s] %d ms" % (self.tag, time_taken))

    def __enter__(self):
        self.start()

    def __exit__(self, type, value, traceback):
        self.stop()

