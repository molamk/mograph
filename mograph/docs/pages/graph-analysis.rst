Graph Analysis
==============

To order services according to their dependencies, the DAG model was the best
fit. `Directed Acyclic Graphs <https://en.wikipedia.org/wiki/Directed_acyclic_graph>`_
are composed of vertices (representing services) and edges (representing dependencies).

Graph Must Be Acyclic
---------------------

For our task, the graph needs to be acyclic. This is because if we do have
a cycle, it becomes impossible to derive an order between dependencies.

For example, this configuration is not valid:

.. code-block:: yaml

    mysql:
        deps:
            - kibana
    kibana:
        deps:
            - mysql


We see that `mysql` relies on `kibana`, but at the same time `kibana` relies
on `mysql`. It becomes impossible to start (or stop) a service because of this.

Graph Must Define All Nodes
---------------------------

In other words, all services in the `yaml` file, need to be defined at "root"
level. Meaning that if a service is mentioned in a "dependency list" but not
defined at "root level", the graph is considered invalid.

This is because we don't know if the service mentioned has any dependencies,
and so we can't figure out its order in the cluster.

Here's an example of an invalid configuration:

.. code-block:: yaml

    mysql:
        deps: []
    kibana:
        deps:
            - elasticsearch

As we see, `kibana` needs `elasticsearch`, but since `elasticsearch` was not
defined at "root" level (only `mysql` & `kibana`), the graph is invalid.

Graph Representation
--------------------

The actual graph was implemented as an `Adjacency Matrix <https://en.wikipedia.org/wiki/Adjacency_matrix>`_.
Each service is given a numerical ID and put in the matrix. This was done to
accelerate the graph's processing, so we "compare" numbers instead of whole strings.

Here's an example of a graph representation:

.. code-block:: yaml

    mysql:
        deps: []
    kibana:
        deps:
            - mysql
    elasticsearch:
        deps:
            - kibana

Its representation looks like this:

.. code-block:: text

    # Name - ID map
    { "mysql": 0, "kibana": 1, "elasticsearch": 2 }

    # Actual Graph
    [ [], [0], [1] ]

If a specification has "missing definitions", it was put in another "pending"
map that linked it to its "dependents".

.. code-block:: yaml

    mysql:
        deps: []
    kibana:
        deps:
            - elasticsearch

Give use the following structure:

.. code-block:: text

    # Name - ID map
    { "mysql": 0, "kibana": 1, "elasticsearch": 2 }

    # Actual Graph
    [ [], [] ]

    # Pending Map
    { 2: [1] }


Cycle Detection
---------------

For this task, I chose the ` Graph Coloring <https://en.wikipedia.org/wiki/Graph_coloring>`_
technique. I prefer this technique because it is intuitive and efficient.

It's a "modified" DFS (Depth First Search) traversal. The colors are:

- White: unprocessed node
- Gray: node is being processed
- Black; node has been processed

Here's how the algorithm works:

- Start with all nodes as "white"
- Choose a node & mark it as "gray"
- For each of its neighbors:
    - If the neighbor is "gray", then it means we've seen it in this traversal, which is equivalent to a cycle
    - If it's "white", but any of it's children has a cycle, then we also have a cycle
    - If neither, all good
- We do this recursively
- At the end of processing a node, mark it as "black"

Missing Definition Detection
----------------------------

This is a trivial task since we already keep a map containing missing
definitions. We just have to check if the map is empty, then we're good.

Dependency Ordering
-------------------

This was also implemented as a "modified DFS traversal", here's how:

- At root, the level is always "0"
- We choose any node
- Do this recursively on its dependencies
- Give current node -> level = max(dep_lvl_1, dep_lvl_2,...) + 1

Since the algorithm is recursive, I also used the "memorization" technique so
we don't process a node multiple times.

Here's an example of execution:

.. code-block:: yaml

    mysql:
        deps: []
    zookeeper:
        deps: []
    kibana:
        deps:
            - mysql
    fullhouse:
        deps:
            - kibana
            - zookeeper

This will give us the following starting sequence:

.. code-block:: text

    ['mysql', 'zookeeper']
    ['kibana']
    ['fullhouse']

Reversing Dependencies for the Stop Sequence
--------------------------------------------

To derive to the stop sequence, we just need to reverse the dependencies.
In other words, we reverse the direction of the edges.

To do that, we just put the new destinations at the place of old origins,
and vice-versa.

Then we call the same method responsible for ordering our dependencies, which
would give us the following stop sequence:

.. code-block:: text

    ['fullhouse']
    ['zookeeper', 'kibana']
    ['mysql']
