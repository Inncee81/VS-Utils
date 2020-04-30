import os, errno, logging
from datetime import datetime
from scope import scope_reverse_map_path

## Get the log name from the project file
cur_dir = os.path.dirname(os.path.abspath(__file__))
par_dir = os.path.join(cur_dir, os.pardir)
project_file = os.path.join(par_dir, ".project")
with open(project_file, 'r') as f: log_name = f.read()

rootLogger = ""

def create_path_directories(path):
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def handler_exists(htype):
    handler = [h for h in rootLogger.handlers if type(h) == htype]
    return bool(handler)

def init_logging(args=None, cfg=None):
    """ Initialize the logging """

    global rootLogger
    logFormatter = ""

    ## Setup the logging file
    if (args != None and cfg != None and args.scope != "postgres"):
        if not os.path.isdir(cfg.log_dir):
            create_path_directories(cfg.log_dir)
        log_file = os.path.join(cfg.log_dir, "{}.log".format(log_name))
        log_file = scope_reverse_map_path(cfg, args, log_file)
        if not os.path.isfile(log_file): open(log_file, 'a').close()

    ## Setup the root logger
    log_lvl = logging.DEBUG if (not args and not cfg) else cfg.log_level
    if (rootLogger == ""):
        logFormatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt='%Y-%m-%d %H:%M:%S')
        rootLogger = logging.getLogger()
        rootLogger.setLevel(log_lvl)

    ## Add a file handler only in non-postgres mode
    if (args != None and cfg != None and args.scope != "postgres"):
        if not handler_exists(logging.FileHandler):
            fileHandler = logging.FileHandler(log_file, mode='a')
            fileHandler.setFormatter(logFormatter)
            fileHandler.setLevel(log_lvl)
            rootLogger.addHandler(fileHandler)

    ## Always add a console handler
    if not handler_exists(logging.StreamHandler):
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(logFormatter)
        consoleHandler.setLevel(log_lvl)
        rootLogger.addHandler(consoleHandler)

def printmsg(message, msgtype, prefix=None, arguments=None):

    global rootLogger

    if arguments:
        print_str = ", ".join(["%s"] * len(arguments))
        if msgtype == "error":
            arguments = (("%-15s- " % prefix),) + ("Error: ", ) + (message,) + arguments
            rootLogger.error(("%s%s%s: (" + print_str + ")") % arguments)
        elif(msgtype == "debug"):
            arguments = (("%-15s- " % prefix),) + (message,) + arguments
            rootLogger.debug(("%s%s: (" + print_str + ")") % arguments)
        else:
            arguments = (("%-15s- " % prefix),) + (message,) + arguments
            rootLogger.info(("%s%s: (" + print_str + ")") % arguments)
    else:
        if msgtype == "error":
            rootLogger.error("%s%s%s" % (("%-15s- " % prefix), "Error: ", message))
        elif(msgtype == "debug"):
            rootLogger.debug("%s%s" % ("%-15s- " % prefix, message))
        else:
            rootLogger.info("%s%s" % ("%-15s- " % prefix, message))


def errmsg(message, prefix="", arguments=None):
    if rootLogger == "": init_logging()
    if (type(prefix) == tuple):
        arguments = prefix
        prefix = ""
    printmsg(message, "error", prefix, arguments)

def infomsg(message, prefix="", arguments=None):
    if rootLogger == "": init_logging()
    if (type(prefix) == tuple):
        arguments = prefix
        prefix = ""
    printmsg(message, "info", prefix, arguments)

def debugmsg(message, prefix="", arguments=None):
    if rootLogger == "": init_logging()
    if (type(prefix) == tuple):
        arguments = prefix
        prefix = ""
    printmsg(message, "debug", prefix, arguments)