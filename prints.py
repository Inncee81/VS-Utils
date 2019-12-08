import sys
from datetime import datetime

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open("/proc/1/fd/1", "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

def printmsg(message, msgtype, arguments=None, redirect=True):
    cur_date = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")

    ## Redirect stdout and stderr for docker logs if necessary
    if redirect:
        sys.stdout, sys.stderr = (Logger() for _ in range(2))

    if arguments:
        print_str = ", ".join(["%s"] * len(arguments))
        if msgtype == "error":
            arguments = (cur_date,) + ("Error: ", ) + (message,) + arguments
            print(("[%s] %s%s: (" + print_str + ")") % arguments)
        else:
            arguments = (cur_date,) + (message,) + arguments
            print(("[%s] %s: (" + print_str + ")") % arguments)
    else:
        if msgtype == "error":
            print("[%s] %s%s" % (cur_date, "Error: ", message))
        else:
            print("[%s] %s" % (cur_date, message))

def errmsg(message, arguments=None):
    printmsg(message, "error", arguments)

def debugmsg(message, arguments=None):
    printmsg(message, "debug", arguments)