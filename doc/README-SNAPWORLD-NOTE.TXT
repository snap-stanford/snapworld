Technical Note on the Snapworld System
Apr 8, 2013


*** Overview ***

The goal of the SnapWorld project is to provide a platform for studying
interactions between all the people on Earth. The plan is to construct
a synthetic graph. The graph has a node for each person on Earth.
There is an edge between the two nodes, if the corresponding persons
are connected, either being friends or through their interactions.

The first project is to investigate different models of graphs generation
and how they impact average distance between the nodes.

The project studies graphs with ~7B nodes and on average 150 edges/node.
150 is assumed to be the value of Dunbar's number.

A cluster of machines is needed to do the computations. The entire graph
is too large to fit in RAM on one machine. Furthermore, there is not enough
RAM available in our cluster for the entire graph.


*** System Overview ***

The system consists of the following tasks:
- user, head, host, work

User task is a client program that is used by the user to communicate
with the system. There is one user task per application.

Head task is the central task that controls the entire execution.
There is one head task per application.

Host tasks control the execution on one host. There is one host task
per compute host.

Work tasks perform one unit of work. There can be many work tasks per
compute host.

User, head and host tasks are the same for all the applications and
provided by the system.

Work tasks have to be written by the user for each application, using
a system provided library for communication with other system tasks.
Several different types of work tasks can be used in the same application.


*** Execution ***

The computation follows the bulk synchronous parallel computation model.
The execution is split into supersteps. Each work task has an input queue
and local storage. Local storage holds any state that needs to be
persistent across the supersteps.

During a superstep, a work task gets its state from the local storage,
reads items from its input queue, performs the computation and places
outputs to input queues for the next step. At the end of the step,
the work task saves any state to its local storage and notifies
the host task that it completed the computation.

Each work task is responsible for specifying a recipient for
the messages that it generates. This means that tasks must know
the names of other tasks, but not their hosts.


*** Task Communications ***

A high level format of tasks is as follows. Head and host tasks are
web services, but can also call other services as clients. User task
is only a web client. Work tasks are user provided programs that
utilize a system provided library to communicate with other tasks.

The tasks use the following communication patterns. A user task calls
the head task. The head task calls host tasks. Host tasks call the head
task. Work tasks call the host tasks using the system library.


*** Web Service API ***

Head Task

- 'start' from user task
	- start all host tasks

- 'get config' from host task
	- send config to host

- step 'done' from host task
	- if all hosts done:
		- if last step:
			- send 'quit' to all host
		- send 'prepare' to all hosts

- step 'ready' from host task
	- if all hosts ready:
		- send step 'start' to all hosts

- 'get executable' from host task
	- send executable, time to a host

- 'quit' from user
	- send 'quit' to all hosts
	- terminate

Host Task

- step 'start' from head task
	- start local tasks

- 'get config' from work task
	- send config to work

- 'put output' from work task
	- store output to dst work queue

- step 'done' from work task
	- if all works done:
		- send step done to master

- step 'prepare' from head task
	- update the queues for the next step
	- send ready to master

- 'quit' from head task
	- terminate


*** Task Description ***

User Task

- read config
- start head
- send set config to head
- send start to head
- while head status not done:
	sleep
- send quit to head

Head Task

- while true:
	service API requests

Host Task

- send get config to head
- send step done to head
- while true:
	service API requests

Work Task

- restore state
- send get config to local host
- while input:
	- process input
	- send output to dst host
- send output to dst host
- save state
- send done to local host


*** Configuration File ***

A sample configuration file is provided below. It is intended
for illustrative purposes only. The actual configuration file
can be different.

----------------------------------------------------

# description of hosts
master	ilcm0
hosts	ilc1,ilc2,ilc3,...

# problem parameters
var	nodes		7,000,000,000
var	range		3,000,000
var	stat_tasks	108
var	gen_tasks	2,334
#var	nodes		7,000,000,000
#var	range		1,048,576
#var	stat_tasks	36
#var	gen_tasks	6,678

# description of work tasks and problem partitioning
bunch	GenTasks	size	1		range	$range
bunch	GenStubs	size	$gen_tasks	range	1
bunch	GenGraph	size	$gen_tasks	range	$range
bunch	GenNbr		size	$gen_tasks	range	1
bunch	GenDist		size	$stat_tasks	range	$range

# topology
route	__Start__	GenTasks
route	GenTasks	GenStubs
route	GenStubs	GenGraph
route	GenGraph	GenNbr
route	GenNbr		GenDist
route	GenDist		GenNbr
----------------------------------------------------


*** Breadth First Search Application ****

GenTasks generates input for GenStubs.

GenStubs determines degrees for all the nodes, generates the stubs and
distributes them.

GenGraph generates the graph edges by randomly selecting pairs of stubs.

GenNbr provides a list of node neighbors.

GetDist keeps the distances.

