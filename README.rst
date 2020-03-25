``mograph``
===========

.. image:: https://img.shields.io/codecov/c/github/molamk/mograph
   :target: https://codecov.io/gh/molamk/mograph
   :alt: codecov
 
.. image:: https://img.shields.io/circleci/build/github/molamk/mograph
   :target: https://circleci.com/gh/molamk/mograph
   :alt: CircleCI
 
.. image:: https://img.shields.io/pypi/v/mograph
   :target: https://badge.fury.io/py/mograph
   :alt: PyPI version
 
.. image:: https://img.shields.io/github/license/molamk/mograph
   :target: https://github.com/molamk/mograph/blob/master/LICENSE
   :alt: License
 
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black
   :alt: Code style: black

.. raw:: html

   <p align="center">
      <a href="https://mograph.readthedocs.io/">
         <img alt="GitPoint" title="GitPoint" src="https://media.giphy.com/media/RJQ9uP1UFnWO5xU9jX/giphy.gif" width="600">
      </a>
   </p>

A dependency graph analysis and processing tool written in Python..

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

Manually from this repository
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can also clone this repository, install its dependencies and run the tool from there.

.. code-block:: bash

   # Clone the repository
   git clone git@github.com:molamk/mograph.git && cd mograph

   # Install the project
   python3 setup.py develop

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

   # or (depending on your configuration)

   python3 -m mograph ./services.yaml

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

Tech Stack
----------

* Implementation in `Python 3 <https://www.python.org/>`_
* CI/CD with `CircleCI <https://circleci.com/>`_
* Test coverage with `CodeCov <https://codecov.io/>`_
* Python package repository `PyPi <https://pypi.org/>`_
* Documentation hosting with `ReadTheDocs <https://readthedocs.org/>`_

License
-------

`MIT <https://choosealicense.com/licenses/mit/>`_
