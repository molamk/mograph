from mograph.cli import cli
from mograph.logger import get_logger
from click import ClickException, Abort

logger = get_logger(__name__)

if __name__ == "__main__":
    """
    Main entry point, fires off the CLI.

    Usage: mograph [OPTIONS] COMMAND [ARGS]...

    A dependency graph analysis tool.

    Options:
    --help  Show this message and exit.

    Commands:
    start  displays the start sequence.
    stop   displays the stop sequence.

    Exception Handling
    ------------------
        click.Abort:
            Catches EOFError & KeyboardInterrupt
        click.ClickException:
            Catches FileError, UsageError & BadParameter
    """
    try:
        cli.main(standalone_mode=False)
    except ClickException as e:
        logger.critical(e)
    except Abort as e:
        logger.error("Program has been aborted - shutting down...")
        logger.critical(e)
