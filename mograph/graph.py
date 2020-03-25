from enum import Enum

from .exceptions import CyclicGraphError, UndefinedProviderError


def config_to_graph(config=None):
    """
    Parses a YAML file's content into a Directed Graph.

    The main algorithm works as follows:

    - Iterate over all services.
    - Add the current service to the graph (as a vertex).
    - If the service has been in the pending list:
        - Add an edge from each of its dependents to it.
        - Remove it from the pending list.
    - If it has dependencies, iterate over all of them.
        - If the dependency is defined:
            - Add an edge from it to the dependency.
        - Else:
            - Add the dependency to the pending list.

    Parameters
    ----------
    config: dict
        The YAML file's content.

    Returns
    -------
    g: Graph
        A dependency graph (that may be invalid).

    """
    if config is None:
        config = {}
    graph = Graph()

    for service_name, service_data in config.items():

        graph.add_consumer(service_name)

        # Handle pending dependencies
        if graph.is_undefined_provider(service_name):
            all_consumers_for_pending_provider = graph.get_consumers_for_undefined_provider(
                service_name
            )

            for consumer_for_pending_provider in all_consumers_for_pending_provider:
                graph.add_dependency(consumer_for_pending_provider, service_name)

            graph.pop_undefined_provider(service_name)

        # Handle dependencies
        if "deps" in service_data:
            dependencies_list = service_data["deps"]

            for dependency in dependencies_list:
                if graph.has_consumer(dependency):
                    graph.add_dependency(service_name, dependency)
                else:
                    graph.add_undefined_provider_for_consumer(dependency, service_name)

    return graph


class VertexColor(Enum):
    """Defines a vertex's color for cycle detection using DFS."""

    WHITE = "Vertex has not been processed yet."
    GRAY = "Vertex is being processed."
    BLACK = "Vertex has been processed."


class Graph:
    """
    Directed Graph implementation.

    In order to represent dependencies between our services, we use a Directed
    Graph. This particular implementation follows the Adjacency Matrix model.

    It supports operations such as:
    - Adding a vertex (service).
    - Adding an edge (dependency).
    - Adding an undefined provider (pending service definition).
    - Detecting if there is a cycle.
    - Detecting if the final graph has missing dependencies.

    Note
    ----
    A quick note about consumers and providers:
    - Consumer: A service that has dependencies.
    - Provider: A service that is a dependency of another service.
    - A consumer can have no providers.
    - A provider must have at least one consumer.
    - All providers are also consumers (need to be defined).
    - Not all consumers are providers.
    
    Attributes
    ----------
    __vertices : list of list of int
        The Adjacency Matrix containing IDs of vertices.
    __undefined_provider_to_consumer_map : dict
        A mapping from undefined (pending) providers to their consumers.
    __id_name_map : dict
        A mapping between a service's ID to its name.

    """

    def __init__(self):
        self.__vertices = []
        self.__undefined_provider_to_consumer_map = dict()
        self.__id_name_map = dict()

    def add_consumer(self, service_name):
        """
        Adds a vertex (service) to the graph.

        Works as follows:
        - Generates an ID for the service (the current length of nodes).
        - Add the vertex to the matrix.

        Parameters
        ----------
        service_name: str
            The name of the service.

        Returns
        -------
        bool
            True if successful, False otherwise.

        """
        self.__id_name_map[service_name] = len(self.__vertices)
        self.__vertices.append([])

    def has_consumer(self, service_name):
        """
        Check if a vertex is in the graph.

        Meaning:
        - Has the service been already defined as a consumer?
        - If the service has been seen in a list of dependencies, it is not
        considered as a vertex yet (pending). 

        Works as follows:
        - Generates an ID for the service (the current length of nodes).
        - Add the vertex to the matrix.

        Parameters
        ----------
        service_name: str
            The name of the service.

        Returns
        -------
        bool
            True if exists in graph, False otherwise.

        """
        return service_name in self.__id_name_map

    def is_undefined_provider(self, service_name):
        """
        Check if a service is pending definitions.

        Meaning:
        - The service has been seen in a list of dependencies.
        - The service has not been defined at root yet.

        Parameters
        ----------
        service_name: str
            The name of the service.

        Returns
        -------
        bool
            True if in the pending map, False otherwise.

        """
        return service_name in self.__undefined_provider_to_consumer_map

    def get_consumers_for_undefined_provider(self, service_name):
        """
        Gets the list of consumers dependent on an undefined provider.

        Parameters
        ----------
        service_name: str
            The name of the undefined provider.

        Returns
        -------
        list of int
            All consumers dependent on the given provider.

        """
        return self.__undefined_provider_to_consumer_map[service_name]

    def add_undefined_provider_for_consumer(self, provider, consumer):
        """
        Adds a service as pending (undefined provider).

        This means that it has been first seen in a dependencies list, but not
        yet at root level.

        Parameters
        ----------
        provider: str
            The name of the undefined provider.
        consumer: str
            The name of the consumer.

        """
        if provider not in self.__undefined_provider_to_consumer_map:
            self.__undefined_provider_to_consumer_map[provider] = []

        self.__undefined_provider_to_consumer_map[provider].append(consumer)

    def pop_undefined_provider(self, service_name):
        """
        Removes a services from the pending list (now defined / seen at root).

        Parameters
        ----------
        service_name: str
            The name of the undefined provider.

        """
        self.__undefined_provider_to_consumer_map.pop(service_name)

    def add_dependency(self, consumer, provider):
        """
        Adds an edge going from the consumer to the provider.

        Parameters
        ----------
        consumer: str
            The name of the consumer.
        provider: str
            The name of the provider.

        """
        consumer_id = self.__id_name_map[consumer]
        provider_id = self.__id_name_map[provider]

        self.__vertices[consumer_id].append(provider_id)

    def has_edge(self, origin, destination):
        """
        Determines if there is an edge between to given vertices in the graph.

        Returns
        -------
        bool
            True if the edge exists, False otherwise.

        """
        return (
            self.__id_name_map[destination]
            in self.__vertices[self.__id_name_map[origin]]
        )

    def get_all_levels(self):
        """
        Determines the layers of the graph to be run in parallel.

        This is responsible for segmenting the graph in different layers
        according to its inner dependencies.

        - Each layer is on a "level" of dependents
        - Each layer is a list of services that can be run in parallel.

        For example, the following YAML configuration;

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

        Have these levels for the "start" sequence:
        - [mysql, zookeeper]
        - [kibana]
        - [fullhouse]

        Returns
        -------
        list of list of str
            Sequence of service batches to be run as start or stop.

        """
        name_id_dict = {v: k for k, v in self.__id_name_map.items()}
        memo = dict()
        level_map = dict()

        for v in range(len(self.__vertices)):
            current_level = self.__get_vertex_level(v, memo)

            if current_level not in level_map:
                level_map[current_level] = []
            level_map[current_level].append(name_id_dict[v])

        in_order = []
        for i in range(len(level_map)):
            in_order.append(level_map[i])

        return in_order

    def __get_vertex_level(self, vertex, memo=None, level=0):
        # Modified DFS (Depth First Search) to calculate each vertex's level.

        # This recursive method uses the memorization technique to avoid
        # unnecessary (duplicate) calls.

        if memo is None:
            memo = dict()
        if vertex in memo:
            return memo[vertex]
        elif not self.__vertices[vertex]:
            memo[vertex] = 0
        else:
            memo[vertex] = (
                max(
                    self.__get_vertex_level(x, memo, level)
                    for x in self.__vertices[vertex]
                )
                + 1
            )

        return memo[vertex]

    def reverse_dependencies(self):
        """
        Reverse a graph's dependencies.

        We use this when we want to switch from "start" sequence to "stop"
        sequence. This method allows us to reverse without having to write
        "start" or "stop" specific algorithms.

        The `get_all_levels()` works for both, and the transition happens
        with `reverse_dependencies()`

        """
        rev_graph = [[] for _ in self.__vertices]

        for i in range(len(self.__vertices)):
            for current_neighbor in self.__vertices[i]:
                rev_graph[current_neighbor].append(i)

        self.__vertices = rev_graph

    def validate(self):
        """
        Validates our graph against the specification.

        This makes sure that the graph is:
        - A DAG (Directed Acyclic Graph) which is necessary condition to order
        its dependencies.
        - A full graph. Meaning that all the services have been defined at
        root level (and not just seen in a dependencies list).

        Raises
        ------
        CyclicGraphError
            If the graph has a cycle.
        UndefinedProviderError
            If some service has a required but undefined dependency.

        """
        if len(self.__undefined_provider_to_consumer_map) != 0:
            provider, consumers = self.__undefined_provider_to_consumer_map.popitem()
            raise UndefinedProviderError(provider, consumers)

        back_edge = self.__get_cycle_if_exists()
        if back_edge is not None:
            raise CyclicGraphError(back_edge[0], back_edge[1])

    def __get_cycle_dfs(self, u, vertices_colors):
        # A modified recursive DFS that uses the Graph Coloring technique
        # to detect cycles in a directed graph.

        vertices_colors[u] = VertexColor.GRAY

        for v in self.__vertices[u]:

            # If the next vertex is already being processed
            if vertices_colors[v] == VertexColor.GRAY:
                return u, v

            # If some subset of 'v' descendants have a back-edge
            if vertices_colors[v] == VertexColor.WHITE:
                back_edge = self.__get_cycle_dfs(v, vertices_colors)
                if back_edge is not None:
                    # Here we return the back-edge so we can have its
                    # details if/when the exception is raised.
                    return back_edge

        vertices_colors[u] = VertexColor.BLACK
        return None

    def __get_cycle_if_exists(self):
        # Detects if there is a cycle within the graph.
        # Resolves the IDs of vertices into names for exception
        # handling purposes.

        vertices_colors = [VertexColor.WHITE] * len(self.__vertices)

        for i in range(len(self.__vertices)):
            if vertices_colors[i] == VertexColor.WHITE:
                back_edge = self.__get_cycle_dfs(i, vertices_colors)
                if back_edge is not None:
                    name_id_dict = {v: k for k, v in self.__id_name_map.items()}
                    origin = name_id_dict[back_edge[0]]
                    destination = name_id_dict[back_edge[1]]
                    return origin, destination

        return None

    def size(self):
        return len(self.__vertices)

    def __repr__(self):
        return repr(self.__vertices)

    def __str__(self):
        name_id_dict = {v: k for k, v in self.__id_name_map.items()}

        services_with_deps_str = []

        for consumer_id, all_providers_ids in enumerate(self.__vertices):
            consumer_name = name_id_dict[consumer_id]
            all_providers_names = [name_id_dict[x] for x in all_providers_ids]

            services_with_deps_str.append(
                "{}: {}".format(consumer_name.ljust(20), all_providers_names)
            )

        return "\n".join(services_with_deps_str)
