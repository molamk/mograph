import sys

import yaml

from .exceptions import CyclicGraphError, UndefinedProviderError
from .graph import config_to_graph
from .logger import get_logger

logger = get_logger(__name__)


def load_and_validate_yaml(stream):
    """
    Reads, analyzes & validates a dependency graph.

    Parameters
    ----------
    stream: StringIO
        The input file stream.

    Returns
    -------
    g: Graph
        A valid dependency graph that reflects the services' spec.

    Exception Handling
    ------------------
    yaml.YAMLError
        When the YAML syntax is invalid, failed parsing.
    UndefinedProviderError
        When a service has an undefined dependency.
    CyclicGraphError
        When a graph has a cycle.

    """
    try:
        content = yaml.safe_load(stream.read())

        g = config_to_graph(content)
        g.validate()

        return g

    except yaml.YAMLError as e:
        logger.error("Invalid YAML syntax: Could not parse content.")
        logger.critical(e)
        sys.exit(1)
    except (UndefinedProviderError, CyclicGraphError) as e:
        logger.error(
            "Invalid specification: All services should be defined & without cycles."
        )
        logger.critical(e)
        sys.exit(1)
