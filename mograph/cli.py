import click

from .logger import get_logger
from .reader import load_and_validate_yaml

logger = get_logger(__name__)


@click.group()
def cli():
    """A dependency graph analysis tool."""


@cli.command("start", short_help="displays the start sequence.")
@click.argument("file_path", type=click.File("r"))
def start(file_path):
    """
    Loads & analyzes services then displays the starting sequence.

    Requirements for starting services:
    - Service can be started if all of its dependencies are started.
    - Multiple services should be started in parallel, if possible.

    Parameters
    ----------
    file_path : str, optional
        Location of the YAML file that specifies a set of services.

    Examples
    --------
    Running the start command

    >>> start
    START SEQUENCE
    0   : ['mysql', 'elasticsearch', 'zookeeper']
    1   : ['hadoop-namenode', 'kibana']
    2   : ['hbase-master']
    3   : ['fullhouse']
    4   : ['dashboard']

    """
    g = load_and_validate_yaml(file_path)

    print("START SEQUENCE\n")
    for i, l in enumerate(g.get_all_levels()):
        print("{} : {}".format(str(i).ljust(3), l))


@cli.command("stop", short_help="displays the stop sequence.")
@click.argument("file_path", type=click.File("r"))
def stop(file_path):
    """
    Loads & analyzes services then displays the stopping sequence.

    Requirements for stopping services:
    - Service can be stopped if all of its dependencies are started.
    - Multiple services should be stopped in parallel, if possible.

    Parameters
    ----------
    file_path : str, optional
        Location of the YAML file that specifies a set of services.

    Examples
    --------
    Running the stop command

    >>> stop
    STOP SEQUENCE
    0   : ['kibana', 'dashboard']
    1   : ['fullhouse']
    2   : ['mysql', 'hbase-master', 'elasticsearch']
    3   : ['hadoop-namenode']
    4   : ['zookeeper']

    """
    g = load_and_validate_yaml(file_path)

    print("STOP SEQUENCE\n")
    g.reverse_dependencies()
    for i, l in enumerate(g.get_all_levels()):
        print("{} : {}".format(str(i).ljust(3), l))
