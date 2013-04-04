Installation and Running of SnapWorld
Apr 4, 2013

# clone the Snapworld github repository:
mkdir git
cd git
git clone https://github.com/snap-stanford/snapworld 

# create a working directory
mkdir work

# prepare your host for execution
# - copy config/snapworld.sh to a directory on the execution path
# - customize snapworld.sh for your configuration, if needed
# - create the execution directory, ${HOME}/snapwexec by default
# - make sure that 'ssh' to your local host does not require a password

# copy required files to the working directory
cp pybfs/* python/* lib/swlib.py libbfs/* ~/git1/snapworld/work

# change the working directory
cd work

# configure Snapworld for your configuration
# - in snapw.config: replace <host> with your computer

# start the head task
python head.py

# in another window, start the application
curl -i http://<host>:8100/start

# the execution should be around 10s

# stop all the SnapWorld processes
curl -i http://<host>:8100/quit

# check out the results in ${HOME}/snapwexec
cat ${HOME}/snapwexec/log-swfinish-*.txt

# you should see something like
Starting task __Finish__-0 with host 0.0.0.0:8120, queue /home/rok/snapwexec/snapw.22994/qact/__Finish__-0
msglist ['GetDist-0']
node 9, distances [1, 9, 36, 54, 1]
finished

# Congratulations!
# You have just successfully executed your first SnapWorld application.

