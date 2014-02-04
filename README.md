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

Running
-------

Below are the steps to install and run Snapworld.
  
    1. % mkdir hanworks; cd hanworks
        In your workspace create a directory called hanworks and change dir. 
    2. % rake setup
        This only needs to be run on initial setup, it pulls the repositiories,
        and builds the project.
    3.  In the snapworld directory open the Rakefile and change HOST_N to
        the number of machines you want to use. This includes the master and
        supervisors, ex. HOST_N=5
    4. % rake test

