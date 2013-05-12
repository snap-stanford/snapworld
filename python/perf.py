import time
import os

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
        # Hack so that func name in log will report `timer` instead of `stop`
        self.timer(tag)

    def timer(self, tag):
        time_taken = time.time() - self.start_times[tag]
        extra = self.extras[tag]
        if extra is not None:
            self.log.info("[%s] (%s) %.2f s" % (str(tag), str(extra), time_taken))
        else:
            self.log.info("[%s] %.2f s" % (str(tag), time_taken))
        del self.start_times[tag]
        del self.extras[tag]

    def update_extra(self, tag, extra):
        self.extras[tag] = extra

    def __enter__(self):
        self.start(self.tag)

    def __exit__(self, type, value, traceback):
        self.stop(self.tag)

    def has_tag(self, tag):
        return tag in self.start_times


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
