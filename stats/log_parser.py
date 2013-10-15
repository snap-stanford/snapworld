import sys
import os
import glob

invalid_input = True
VALID_CHOICES = ["master", "supervisor"]
SINGLE_FILE = True

"Global store of features as key/values"
data = {}

def process_supervisor_sys_stats(line):
    """
    Want to match lines of this format:
    [2013-10-14 15:08:10,467] [INFO] [3938] [supervisor.py] [timed_sys_stats_reporter] [sys_stats] (cpu_idle 67072360113)
    """
    line_data = line.split()
    if len(line_data) < 7:
        return
    time_str = line_data[0][1:] + "-" + line_data[1][:-1]
    feature = "sys_stats-%s-%s" % (time_str, line_data[7][1:])
    data[feature] = line_data[8][:-1]

def process_supervisor_timer(line):
    """
    Want to match the following lines:
    [2013-10-13 15:53:12,262] [INFO] [4211] [perf.py] [timer] [superstep-13-overall: GetNbr] 7.82 s
    [2013-10-13 15:53:12,843] [INFO] [4211] [perf.py] [timer] [prog-0] (step: 14, pid: 14002, prog: GetDistCpp2.py) 0.44 s
    """
    line_data = line.split()
    if len(line_data) < 7:
        return
    line_data = line_data[6:]
    line_data_str = line_data.__str__()
    if "step" in line_data_str and "pid" in line_data_str and "prog" in line_data_str:
        prog = line_data[0]
        step_n = line_data[2]
        pid = line_data[4]
        prog_name = line_data[6]
        time = line_data[7]
        # Populates superstep-%d-prog-%d-pid-%d-
        feature = "superstep-%s-%s-pid-%s-%s" % (step_n[:-1], prog[1:-1], pid[:-1], prog_name[:-1])
        data[feature] = time
    else:
        super_step_overall = line_data[0]
        super_step_name = line_data[1]
        time = line_data[2]
        feature = super_step_overall[1:-1] + "-local-" + super_step_name[:-1]
        # Populates "superstep-%d-overall-local-<TaskName>: %d (time in s)"
        data[feature] = time

def process_supervisor_cum_timer(line):
    """
    Trying to match:
    [2013-10-13 16:29:05,396] [INFO] [20668] [perf.py] [cum_timer] [network] 0.00 s
    """
    line_data = line.split()
    pid = line_data[3][1:-1]
    resource = line_data[6][1:-1]
    time = line_data[7]
    feature = "%s-time-pid-%s" % (resource, pid)
    data[feature] = time

def process_master(filename):
    with open(filename) as f:
        for line in f:
            if "timer" in line and "step" in line:
                line_data = line.split()
                # Stores the superstep-%d-host-%d : time (s)
                data[line_data[6][1:-1]] = line_data[7]

def process(filename, mode):
    if mode == "supervisor":
        for log_file in glob.glob('/lfs/local/0/' + os.environ["USER"] + '/supervisors/*/execute/supervisor-sh-*'):
            with open(log_file) as f:
                for line in f:
                    if "[timer]" in line:
                        process_supervisor_timer(line)
                    elif "[cum_timer]" in line:
                        process_supervisor_cum_timer(line)
                    elif "[sys_stats" in line:
                        process_supervisor_sys_stats(line)
                # Just parse one file/supervisor log.
                if SINGLE_FILE:
                    break
    else:
        process_master(filename)


if __name__ == '__main__':
    if len(sys.argv) > 2:
        mode = sys.argv[1]
        invalid_input = not (mode in VALID_CHOICES)
        filename = sys.argv[2]
        if invalid_input:
            print "Usage: python log_parser.py [master|supervisor] <log_directory>"
            sys.exit(1)
        process(filename, mode)
        for k, v in data.items():
            print k + "\t" + v

