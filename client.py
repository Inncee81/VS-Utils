import os, re, urllib
import socket, fcntl, struct

from urllib.request import urlopen
from urllib.parse import urlencode
from prints import errmsg, debugmsg, infomsg

def client_get_ip_address(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(s.fileno(), 0x8915, struct.pack('256s', bytes(ifname[:15], 'utf-8')))[20:24])

def client_get_default_gateway():
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2: continue
    return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

def client_get_url(scope, port):
    ip = client_get_default_gateway() if scope == "docker" else client_get_ip_address('lo')
    return "http://{ip}:{port}/synoindex?".format(ip=ip, port=port)

### Synoindex-Client
def client(scope, port, source_host, output_host=None, original_host=None, original_mode=0):

    ## Get the URL to the Syno-Index server and add the arguments
    url = client_get_url(scope, port)
    if not output_host:
        query_vars = {'source_host': source_host}
    else:
        query_vars = {"source_host": source_host, "output_host": output_host, "original_host": original_host}
    query_vars["original_mode"] = original_mode

    ## Call the url and get the answer of the server
    url = url + urlencode(query_vars)
    infomsg("  Source", "SynoClient", (source_host,))
    infomsg("  Handbrake Output", "SynoClient", (output_host,))
    infomsg("  Original", "SynoClient", (original_host,))
    infomsg("  Original mode", "SynoClient", (original_mode,))
    try:
        contents = urlopen(url).read()
        debugmsg("SynoIndex-Server answered with", "SynoClient", (contents.decode("UTF-8"),))
    except urllib.error.URLError:
        errmsg("Server is not started yet, start the Triggered Task with the right mode"); exit()
