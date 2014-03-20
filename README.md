Snapworld++
===========

Improved Distributed Graph Processing

System Requirements
-------------------

* > Python 2.6.6
* > Ruby 1.8.7 (with Rake)
* gnuplot (To prevent `snap` from printing spurious error messages)
* swig (For `snap-python`)
* nodejs (For running the broker)

Installing
-------

Below are the steps to install Snapworld.

    1.  Setup your SSH keys for GitHub, instructions can be found here:
        https://help.github.com/articles/generating-ssh-keys
    2. % mkdir hanworks; cd hanworks
        In your workspace create a directory called hanworks and change dir. 
    3. % git clone git@github.com:snap-stanford/snapworld.git
        Clone the snapworld repository.
    4. % cd snapworld; rake setup
        This only needs to be run on initial setup, it pulls the other
        necessary repositiories, and builds the project.

Running
-------

Below are the steps to install and run Snapworld.
  
    1.  In the snapworld directory open the Rakefile and change HOST_N to
        the number of machines you want to use. This number is a total and 
        includes the master and supervisors, ex. HOST_N=5
    2.  In the snapworld directory open the snapw.config and configure
        the parameters for your test. Specifically make sure to modify the
        hosts list to only include the machines you want to use. Also set the
        other parameters (nodes, range, stat_tasks, gen_tasks, drange).
    3. % rake test
        In the snapworld directory kickoff the test with rake test.

Stopping
-------

To stop a job type do the following.

    1. % rake cleanup
        This command will kill all of the processes running on all of the
      machines.

Metrics
-------

To view metrics graphs associated with a given run, log your iln01 snapword repo and

    1. % cd python
        Currently it has to be run from this directory.
    2. % ./log_parser process_run -f PATH_OF_master.log_FILE
        Run using ./log_parser instead of python log_parser to make sure
        it uses the correction version of Python. This file currently
        assumes that you are running supervisors on 4 machines, iln02-05.
    3. Now it will suggest a command for you to use to copy the output
       placed in the newly created web_deploy folder onto a server. (scp ...)
