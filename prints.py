import sys
from datetime import datetime

def printmsg(message, msgtype, arguments=None, redirect=True):
    cur_date = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M-%S")

    ## Redirect stdout and stderr for docker logs if necessary
    if redirect:
        sys.stdout = open("/proc/1/fd/1", "w")
        sys.stderr = open("/proc/1/fd/1", "w")

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