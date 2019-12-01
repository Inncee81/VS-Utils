from datetime import datetime

def printmsg(message, msgtype, arguments=None):
	cur_date = datetime.strftime(datetime.now(), "%Y-%m-%d-%H-%M")

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