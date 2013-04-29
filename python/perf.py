import time

class Timer(object):
    def __init__(self, log, tag=None):
        self.log = log
        self.tag = tag
        self.start_times = {}
        self.extras = {}

    def start(self, tag, extra=None):
        self.start_times[tag] = time.time()
        self.extras[tag] = extra

    def stop(self, tag):
        time_taken = time.time() - self.start_times[tag]
        extra = self.extras[tag]
        if extra is not None:
            self.log.debug("[timer] [%s] (%s) %d ms" % (str(tag), str(extra), time_taken))
        else:
            self.log.debug("[timer] [%s] %d ms" % (str(tag), time_taken))
        del self.start_times[tag]
        del self.extras[tag]

    def update_extra(self, tag, extra):
        self.extras[tag] = extra

    def __enter__(self):
        self.start(self.tag)

    def __exit__(self, type, value, traceback):
        self.stop(self.tag)

