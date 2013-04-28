Installation and Running of SnapWorld
Apr 4, 2013

#
# ----- all Python version
#

# clone the Snapworld github repository
mkdir git
cd git
git clone https://github.com/snap-stanford/snapworld 

# create a working directory
mkdir work
cd work

# prepare your host for execution
# - copy config/snapworld.sh to a directory on the execution path
# - customize snapworld.sh for your configuration, if needed
# - create the execution directory, ${HOME}/snapwexec by default
# - make sure that 'ssh' to your local host does not require a password

# copy required Snapworld files to the working directory
cp ../snapworld/pybfs/* ../snapworld/python/* ../snapworld/lib/swlib.py ../snapworld/libbfs/* .

# configure Snapworld for your configuration
# - in snapw.config: replace <host> with your computer

# start the head task
python head.py

# in another window, start the application
curl -i http://<host>:8100/start

# the execution takes around 10s

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

#
# ----- combined Python/SNAP version
#

# install and execute the Python version as described above

# clone the SNAP and SNAP Python repositories
cd git
git clone https://github.com/snap-stanford/snap 
git clone https://github.com/snap-stanford/snap-python

# compile SNAP for use with Python (requires installed swig)
cd snap-python/swig-sw
make

# create a working directory
cd ..
mkdir work1
cd work1

# copy required SNAP Python files to the working directory
cp ../snap-python/swig-sw/_snap.so ../snap-python/swig-sw/snap.py .

# copy required Snapworld files to the working directory
cp ../snapworld/cppbfs/* ../snapworld/python/* ../snapworld/lib/swlib.py ../snapworld/libbfs/* .

# configure Snapworld for your configuration
# - in snapw.config: replace <host> with your computer

# start the head task
python head.py

# in another window, start the application
curl -i http://<host>:8100/start

# the execution takes around 1 min

# stop all the SnapWorld processes
curl -i http://<host>:8100/quit

# check out the results in ${HOME}/snapwexec
cat ${HOME}/snapwexec/log-swfinish-*.txt

# you should see something like
# (notice that the output is from 2 files in this case)
Starting task __Finish__-0 with host 0.0.0.0:8120, queue /home/rok/snapwexec/sna
pw.9089/qact/__Finish__-0
msglist ['GetDist-0', 'GetDist-8']
node 42248, distances [1, 9, 64, 464, 3263, 20275, 61470, 14454]
node 64004, distances [1, 10, 64, 456, 3157, 19729, 61249, 15334]
finished
Starting task __Finish__-0 with host 0.0.0.0:8120, queue /home/rok/snapwexec/sna
pw.9089/qact/__Finish__-0
msglist ['GetDist-5', 'GetDist-4', 'GetDist-7', 'GetDist-3', 'GetDist-9', 'GetDi
st-6', 'GetDist-2', 'GetDist-1']
node 42507, distances [1, 8, 54, 373, 2627, 16815, 59118, 20999, 5]
node 10547, distances [1, 7, 51, 382, 2681, 17111, 59436, 20325, 6]
node 89545, distances [1, 9, 59, 416, 2911, 18277, 60455, 17871, 1]
node 75197, distances [1, 8, 53, 377, 2670, 16966, 59342, 20580, 3]
node 85900, distances [1, 7, 49, 348, 2446, 15789, 57995, 23358, 7]
node 93001, distances [1, 8, 55, 388, 2730, 17444, 59803, 19568, 3]
node 34777, distances [1, 8, 57, 412, 2861, 18077, 60264, 18317, 3]
node 88939, distances [1, 6, 44, 298, 2105, 13711, 54815, 28991, 29]
finished

# Congratulations!
# You have just successfully executed a SnapWorld application that uses SNAP.

