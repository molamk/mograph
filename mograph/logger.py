import logging
import logging.config

import coloredlogs

coloredlogs.install()


def get_logger(name):
    return logging.getLogger(name)
