Network Traffic Benchmark
May 9, 2013

*** How to run ***

# start host.py in one shell
python /home/rok/git/snapworld/work/host.py -i 1 -p 8120

# execute 100 copies, at most 10 concurrently, 'Vec-1M.txt' is file on the disk
time seq 100 | parallel -n0 -j10 python testnet.py -p 8120 -f Vec-1M.txt

# repeat with different input parameters

*** Make the change in the code ***

- wrap a retry around the h.connect() line in client.py:messagevec()

*** Some results ***

# 20x 400Mb, 110Mb/s, 6Gb RAM available
time seq 20 | parallel -n0 -j20 python testnet.py -p 8120 -f Vec-100M.txt
real	1m13.276s

# 30x 400Mb, < 1Gb RAM available, *** one failed to connect ***
time seq 30 | parallel -n0 -j30 python testnet.py -p 8120 -f Vec-100M.txt
real	5m4.413s

# 30x 40Mb
time seq 30 | parallel -n0 -j30 python testnet.py -p 8120 -f Vec-10M.txt
real	0m4.476s

# 40x 40Mb
time seq 40 | parallel -n0 -j40 python testnet.py -p 8120 -f Vec-10M.txt
real	0m4.993s

# 400x 40Mb
time seq 400 | parallel -n0 -j40 python testnet.py -p 8120 -f Vec-10M.txt
real	2m17.065s

# 1000x 40Mb
time seq 1000 | parallel -n0 -j100 python testnet.py -p 8120 -f Vec-10M.txt
real	6m15.559s

# 1000x 40Mb, *** 14 failed to connect ***
time seq 1000 | parallel -n0 -j200 python testnet.py -p 8120 -f Vec-10M.txt
real	7m23.632s

