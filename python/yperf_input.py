#!/usr/bin/env python2.7
# pylint: disable-msg=C0103, C0111
""" This generates a json file containing information about what yperf record
to generate. """

import json
import datetime
from time import mktime

SECS_PER_HOUR = 3600

def get_yperf_name(tm):
    """ Returns the file prefix that would correspond to a certain struct
    datetime t. """
    return 'yperf-' + tm.strftime('%Y%m%d-%H')

def get_step_timestamps(filename):
    """ Returns the start time, followed by the time at which each superstep completed. """
    steps = []
    line_number = 0
    with open(filename) as f:
        for line in f:
            if line_number == 1 or "all hosts completed" in line:
                if line_number == 1 and ('Starting head server on port' not in line or steps):
                    print(' *WARNING* First timestamp for file {0} in unexpected location.'.format(filename))
                line_data = line.split()
                # Stores the superstep-%d-host-%d : time (s)
                steps.append(datetime.datetime.strptime(line_data[0][1:] + ' ' +\
                    line_data[1].split(',')[0], '%Y-%m-%d %H:%M:%S'))
            line_number += 1
    return steps

def dump_json(json_data, f_name):
    """Writes json to file name using space-efficient sperators.
    """
    SEPARATORS = (',',':')
    if f_name is not None:
        with open(f_name, 'w') as f:
            json.dump(json_data, f, separators=SEPARATORS)
    else:
        print json.dumps(json_data, separators=SEPARATORS)

def get_run_info(master_log_name):
    with open(master_log_name) as f:
        line = f.readline()
        return json.loads(
            line[line.find('{'):]
                .replace("'", '"')
                .replace('True', 'true')
                .replace('False', 'false')
        )

def get_times(times):
    return [mktime(t.timetuple()) for t in times]

def process_run(master_log_name, res_file_name, message):
    times = get_step_timestamps(master_log_name)
    run_info = get_run_info(master_log_name)
    run_name = 'metrics-' + times[0].strftime('%Y%m%d-%H%M%S') #TODO add nodes, hours
    ind_json = {}
    ind_json['step_times'] = get_times(times)
    ind_json['meta_data'] = run_info
    ind_json['run_name'] = run_name
    if message is not None:
        ind_json['message'] = message
    dump_json(ind_json, res_file_name)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('filename_master',
            help = 'Path to snapworld master log.')
    parser.add_argument('-r', '--result_file',
            help = 'Path to store result (the future input to a yperf gen_report.py).')
    parser.add_argument('-m', '--message',
            help = 'A message you would like to be stored with this file.')
    args = parser.parse_args()

    process_run(args.filename_master, args.result_file, args.message)
