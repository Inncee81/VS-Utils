import os, sys, errno, logging

from files import create_path_directories
from datetime import datetime

logger = ""

def init_logging(args):
    """ Initialize the logging """

    global logger

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
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

def printmsg(message, msgtype, prefix=None, arguments=None):

    global logger
    cur_date = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")

    if arguments:
        print_str = ", ".join(["%s"] * len(arguments))
        if msgtype == "error":
            arguments = (cur_date,) + (("%-15s- " % prefix),) + ("Error: ", ) + (message,) + arguments
            print(("[%s] %s%s%s: (" + print_str + ")") % arguments)
            logger.error(("[%s] %s%s%s: (" + print_str + ")") % arguments)
        else:
            arguments = (cur_date,) + (("%-15s- " % prefix),) + (message,) + arguments
            print(("[%s] %s%s: (" + print_str + ")") % arguments)
            logger.info(("[%s] %s%s: (" + print_str + ")") % arguments)
    else:
        if msgtype == "error":
            print("[%s] %s%s%s" % (cur_date, ("%-15s- " % prefix), "Error: ", message))
            logger.error("[%s] %s%s%s" % (cur_date, ("%-15s- " % prefix), "Error: ", message))
        else:
            print("[%s] %s%s" % (cur_date, "%-15s- " % prefix, message))
            logger.info("[%s] %s%s" % (cur_date, "%-15s- " % prefix, message))

def errmsg(message, prefix="", arguments=None):
    if (type(prefix) == tuple):
        arguments = prefix
        prefix = ""
    printmsg(message, "error", prefix, arguments)

def debugmsg(message, prefix="", arguments=None):
    if (type(prefix) == tuple):
        arguments = prefix
        prefix = ""
    printmsg(message, "debug", prefix, arguments)