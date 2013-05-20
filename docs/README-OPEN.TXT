Snapworld Open Questions
Apr 26, 2013

- logging
	- now excessively large to support Snapworld development
	- make logging suitable for Snapworld users

- cleanup of execution information
	- now all the execution information (messages, logs) is preserved
	- devise a method to preserve/cleanup the execution information

- performance monitoring
	- now there is no performance monitoring
	- collect performance information during the execution

-------------------------

- partition size
	- now determined by source "bunch range" in snapw.config
	- determine the partition size by destination

- configuration information
*** in progress
	- now sent as a one large message from head to host to worker tasks
	- optimize how the configuration is handled

- support for heterogeneous C++ environments
	- now only homogeneous C++ environments are supported 
	- add support for heterogeneous C++ environments on execution hosts

- worker task scheduling, DONE
	- now the tasks are scheduled sequentially
	- execute the tasks concurrently

- results
	- now the final results are stored ad-hoc
	- make it easy for the user to receive the results

- user execution monitoring
	- now only two commands are implemented: start and quit
	- add execution monitoring capability for the user

- support for graphs with 7B nodes
	- now 32-bits are used, which limits nodes to 2^30 (to be safe)
	- add node segments to the BFS application to support larger graphs
		- note: this is an application change, not a system change

