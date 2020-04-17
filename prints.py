import os, sys, errno, logging, argparse

from datetime import datetime

logger, logger_file = ("" for _ in range(2))

def create_path_directories(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def init_logging(args, cfg):
    """ Initialize the logging """

    global logger
    level = logging.getLevelName(cfg.log_level)

    ## If postgres logging is enabled, there is no log file
    if (args.scope == "postgres"):
        logger = logging.getLogger(__name__)
        logger.setLevel(level)
        return

    ## Check whether the data mapping exists
    if (args.scope == "docker"):
        log_dir = os.path.abspath(os.path.join(args.script_dir, os.pardir, "logs"))
    else:
        log_dir = os.path.abspath(os.path.join(args.script_dir, "logs"))
    if not os.path.isdir(log_dir):
        create_path_directories(log_dir)

    ## Setup the logging files
    log_file = os.path.join(log_dir, "logging.log")
    if not os.path.isfile(log_file): open(log_file, 'a').close()

    ## Setup the logging format
    logging.basicConfig(filename=log_file, filemode='a', format='%(message)s')
    logger_file = log_file
    logger = logging.getLogger(__name__)
    logger.setLevel(level)
    return

def printmsg(message, msgtype, prefix=None, arguments=None):

    global logger
    cur_date = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")

    if arguments:
        print_str = ", ".join(["%s"] * len(arguments))
        if msgtype == "error":
            arguments = (cur_date,) + (("%-15s- " % prefix),) + ("Error: ", ) + (message,) + arguments
            print(("[%s] %s%s%s: (" + print_str + ")") % arguments)
            if logger_file != "":
                logger.error(("[%s] %s%s%s: (" + print_str + ")") % arguments)
        elif(msgtype == "debug"):
            arguments = (cur_date,) + (("%-15s- " % prefix),) + (message,) + arguments
            print(("[%s] %s%s: (" + print_str + ")") % arguments)
            if logger_file != "":
                logger.debug(("[%s] %s%s: (" + print_str + ")") % arguments)
        else:
            arguments = (cur_date,) + (("%-15s- " % prefix),) + (message,) + arguments
            print(("[%s] %s%s: (" + print_str + ")") % arguments)
            if logger_file != "":
                logger.info(("[%s] %s%s: (" + print_str + ")") % arguments)
    else:
        if msgtype == "error":
            print("[%s] %s%s%s" % (cur_date, ("%-15s- " % prefix), "Error: ", message))
            if logger_file != "":
                logger.error("[%s] %s%s%s" % (cur_date, ("%-15s- " % prefix), "Error: ", message))
        elif(msgtype == "debug"):
            print("[%s] %s%s" % (cur_date, "%-15s- " % prefix, message))
            if logger_file != "":
                logger.debug("[%s] %s%s" % (cur_date, "%-15s- " % prefix, message))
        else:
            print("[%s] %s%s" % (cur_date, "%-15s- " % prefix, message))
            if logger_file != "":
                logger.info("[%s] %s%s" % (cur_date, "%-15s- " % prefix, message))

def bootstrap_logging():
    global logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

def errmsg(message, prefix="", arguments=None):
    if isinstance(logger, str):
        bootstrap_logging()
    if (type(prefix) == tuple):
        arguments = prefix
        prefix = ""
    printmsg(message, "error", prefix, arguments)

def infomsg(message, prefix="", arguments=None):
    if isinstance(logger, str):
        bootstrap_logging()
    if (type(prefix) == tuple):
        arguments = prefix
        prefix = ""
    printmsg(message, "info", prefix, arguments)

def debugmsg(message, prefix="", arguments=None):
    if isinstance(logger, str):
        bootstrap_logging()
    if (type(prefix) == tuple):
        arguments = prefix
        prefix = ""
    printmsg(message, "debug", prefix, arguments)