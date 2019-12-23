import os, sys, errno, logging
from datetime import datetime

logger = ""

def init_logging():
    """ Initialize the logging """

    ## Check whether the data mapping exists
    global logger
    data_dir = os.path.join(os.sep, "data")
    if not os.path.isdir(data_dir):
        errmsg("data mount is not available, add it to docker mapping")
        exit()

    ## Check whether the logging directory exist otherwise create it
    logs_dir = os.path.join(data_dir, "logs")
    if  not os.path.isdir(logs_dir):
        os.mkdir(logs_dir)

    ## Setup the logging files
    log_file = os.path.join(logs_dir, "logging.log")
    if not os.path.isfile(log_file): open(log_file, 'a').close()

    ## Setup the logging format
    logging.basicConfig(filename=log_file, filemode='a', format='%(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

def printmsg(message, msgtype, arguments=None):

    global logger
    cur_date = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")

    if arguments:
        print_str = ", ".join(["%s"] * len(arguments))
        if msgtype == "error":
            arguments = (cur_date,) + ("Error: ", ) + (message,) + arguments
            print(("[%s] %s%s: (" + print_str + ")") % arguments)
            logger.error(("[%s] %s%s: (" + print_str + ")") % arguments)
        else:
            arguments = (cur_date,) + (message,) + arguments
            print(("[%s] %s: (" + print_str + ")") % arguments)
            logger.info(("[%s] %s: (" + print_str + ")") % arguments)
    else:
        if msgtype == "error":
            print("[%s] %s%s" % (cur_date, "Error: ", message))
            logger.error("[%s] %s%s" % (cur_date, "Error: ", message))
        else:
            print("[%s] %s" % (cur_date, message))
            logger.info("[%s] %s" % (cur_date, message))

def errmsg(message, arguments=None):
    printmsg(message, "error", arguments)

def debugmsg(message, arguments=None):
    printmsg(message, "debug", arguments)