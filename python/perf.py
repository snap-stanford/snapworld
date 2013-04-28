import time

class Timer(object):
    def __init__(self, log, tag=None):
        self.log = log
        self.tag = tag
        self.start_times = {}

    def start(self, tag=None):
        self.start_times[tag] = time.time()

    def stop(self, tag=None):
        time_taken = time.time() - self.start_times[tag]
        self.log.debug("[timer] [%s] %d ms" % (tag, time_taken))
        del self.start_times[tag]

    def __enter__(self):
        self.start(self.tag)

    def __exit__(self, type, value, traceback):
        self.stop(self.tag)

