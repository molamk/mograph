Error Handling
==============

While executing, our program may run into various errors. To handle that
correctly, it's important to know what they are.

Graph Exceptions
----------------

Cyclic Graph Error
^^^^^^^^^^^^^^^^^^

This exception is raised when we detect a cycle in our graph. This means that
it is not valid, and we cannot determine a valid ordering between its dependencies.

Undefined Service Error
^^^^^^^^^^^^^^^^^^^^^^^

This is raised when a service has been seen as a dependency but not defined
at "root" level. Meaning that we don't have enough information to determine
its order in our dependencies.

File IO Exceptions
------------------

File Not Found Error
^^^^^^^^^^^^^^^^^^^^

Raised when we give a path to a non-existing file to our program.

YAML Parsing Error
^^^^^^^^^^^^^^^^^^

When the file does exist, but it is not compliant with the YAML specification.
This prevents us from parsing its contents, and thus determining an ordering.

CLI / User Exceptions
---------------------

Abort
^^^^^

Raised when we stop the program manually (if we have a huge file, and we have
the time to stop it).

Usage Errors
^^^^^^^^^^^^

Happen when we give a bad parameter to our CLI, or if we don't give any.

Logging
-------

All of these exceptions are fatal, and no meaningful recovery can be executed.
We log them with a timestamp, the caller module and the exception's details.
