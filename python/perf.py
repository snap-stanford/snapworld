import time
import os
import threading

class Timer(object):
    def __init__(self, log, tag=None, thread_safe=False):
        self.log = log
        self.tag = tag
        self.start_times = {}
        self.extras = {}
        self.thread_safe = thread_safe
        if self.thread_safe:
            self.lock = threading.Lock()

    def start(self, tag, extra=None):
        if self.thread_safe:
            self.lock.acquire()
        self.start_times[tag] = time.time()
        self.extras[tag] = extra
        if self.thread_safe:
            self.lock.release()

    def stop(self, tag):
        # Hack so that func name in log will report `timer` instead of `stop`
        self.timer(tag)

    def timer(self, tag):
        if self.thread_safe:
            self.lock.acquire()
        time_taken = time.time() - self.start_times[tag]
        extra = self.extras[tag]
        del self.start_times[tag]
        del self.extras[tag]
        if self.thread_safe:
            self.lock.release()
        if extra is not None:
            self.log.info("[%s] (%s) %.2f s" % (str(tag), str(extra), time_taken))
        else:
            self.log.info("[%s] %.2f s" % (str(tag), time_taken))

    def update_extra(self, tag, extra):
        if self.thread_safe:
            self.lock.acquire()
        self.extras[tag] = extra
        if self.thread_safe:
            self.lock.release()

    def __enter__(self):
        self.start(self.tag)

    def __exit__(self, type, value, traceback):
        self.stop(self.tag)

    def has_tag(self, tag):
        if self.thread_safe:
            self.lock.acquire()
        got_tag = tag in self.start_times
        if self.thread_safe:
            self.lock.release()
        return got_tag


def _get_dir_size(target_dirpath):
    """
    Sums up only files size, and does not include directory metadata size
    Returns size in bytes
    """
    cur_size = 0
    for dirpath, dirnames, filenames in os.walk(target_dirpath):

        for f in filenames:
            path = os.path.join(dirpath, f)
            if os.path.exists(path):
                cur_size += os.path.getsize(path)
    return cur_size

def DirSize(log, dirpath, tag):
    num_bytes = _get_dir_size(dirpath)
    log.info("[%s] %.2f MB" % (str(tag), num_bytes/1048576.0))
