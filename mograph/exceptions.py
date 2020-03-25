class CyclicGraphError(Exception):
    """Error raised when a cycle is detected in the dependency graph.

    In order to "sort" dependencies in the graph, it needs to be a DAG
    (Directed Acyclic Graph).
    
    This is because if there's a cycle, we can not determine which nodes comes
    before which and thus ordering becomes impossible.

    We can represent this cycle with a back-edge, by specifying its origin
    and destination vertices.

    An example of cyclic dependency graph specification would be:
   
    .. code-block:: yaml

        mysql:
            deps:
                - "kibana"
        kibana:
            deps:
                - "mysql"

    Attributes
    ----------
    origin : str
        The origin end of the back-edge causing the cycle.
    destination : str
        The destination end of the back-edge causing the cycle.
    message : :obj:`str`, optional
        Human readable string describing the exception.

    """

    def __init__(self, origin, destination, message=None):
        self.origin = origin
        self.destination = destination

        if message is None:
            message = "A back-edge has between detected from '{}' to '{}'".format(
                origin, destination
            )

        super(CyclicGraphError, self).__init__(message)


class UndefinedProviderError(Exception):
    """Error raised when a service has an undefined dependency.

    In order for the dependency graph to be valid, all dependencies must be
    defined in the YAML specification.

    Let's say we have a specification that looks like this:
    
    .. code-block:: yaml

        mysql:
            deps: []
        dashboard:
            deps:
                - "kibana"
    
    Here we can see that the service `dashboard` requires `kibana`, but
    `kibana` is not defined as a service.

    Attributes
    ----------
    provider : str
        The undefined service required by its dependent.
    consumers : str
        The service that requires the undefined dependency.
    message : :obj:`str`, optional
        Human readable string describing the exception.

    """

    def __init__(self, provider, consumers, message=None):
        self.consumers = consumers
        self.provider = provider

        if message is None:
            message = "The service '{}' is required by {} but not defined".format(
                provider, consumers
            )

        super(UndefinedProviderError, self).__init__(message)
