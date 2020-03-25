Getting Started
===============

To get started with `mograph`, make sure you have an updated version of:

- `python3`
- `pip3`

An environment isolation tool is very nice to have. For this project, `pipenv`
was chosen to ensure a robust virtual environment.

Motivation
----------

In a `micro-services <https://microservices.io/>`_ scenario, we usually have multiple services with various dependencies. This give us many advantages such as loose coupling, high maintainability & testability.

On the other hand, it brings on its own **complexity**. Services have multiple dependencies between each other, and it can quickly get difficult to manage.

Introduction
------------

This tool allows us to scan a services' spec, then determine in what order we can **start** them or **stop** them. In order to make things faster, we can start or stop them in parallel in some cases. Namely:


* Services should be started in parallel if all their dependencies (if any) have already started.
* Services should be stopped in parallel if all their dependents (if any) have already stopped.

Installation
------------

From the PyPi repository
^^^^^^^^^^^^^^^^^^^^^^^^

Use the package manager ``pip`` to install `mograph <https://pypi.org/project/mograph/>`_.

.. code-block:: bash

   pip install mograph

Manually from Github
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also clone the Github repository, install its dependencies and run the tool from there.

.. code-block:: bash

   # Clone the repository
   git clone git@github.com:molamk/deps.git && cd deps

   # Install dependencies
   pip install -r requirements.txt

Usage
-----

The program works as follows:


#. Load a ``yaml`` file describing some services with dependencies.
#. Analyze the dependencies and build the graph.
#. Print the starting (or stopping) sequence.

The ``yaml`` file looks something like this:

.. code-block:: yaml

   # services.yaml

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

To run the program, invoke it with either the ``start`` command or ``stop``\ :

.. code-block:: bash

   mograph start ./services.yaml

The output should be:

.. code-block:: text

   START SEQUENCE

   0   : ['mysql', 'zookeeper']
   1   : ['kibana']
   2   : ['fullhouse']

And for the stop command, it should look like this:

.. code-block:: text

   STOP SEQUENCE

   0   : ['fullhouse']
   1   : ['zookeeper', 'kibana']
   2   : ['mysql']
