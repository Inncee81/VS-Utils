import os, re, urllib
from urllib.request import urlopen
from urllib.parse import urlencode
from prints import errmsg, debugmsg, infomsg

def client_get_url(scope, port):
    if (scope == "docker"):
        import subprocess
        ps = subprocess.Popen(('ip', 'route', 'show'), stdout=subprocess.PIPE)
        output = subprocess.check_output(('grep', 'default'), stdin=ps.stdout)
        ps.wait()
        ip = re.search(r'([0-9]{1,3}[\.]){3}[0-9]{1,3}', output.decode('utf-8'), flags=0).group()
    else:
        import netifaces as ni
        ni.ifaddresses('lo')
        ip = ni.ifaddresses('lo')[ni.AF_INET][0]['addr']

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
    infomsg("Send query to SynoIndex-Server", "SynoClient")
    debugmsg("  Url", "SynoClient", (url,))
    infomsg("  Source", "SynoClient", (source_host,))
    infomsg("  Handbrake Output", "SynoClient", (output_host,))
    infomsg("  Original", "SynoClient", (original_host,))
    infomsg("  Original mode", "SynoClient", (original_mode,))
    try:
        contents = urlopen(url).read()
        debugmsg("SynoIndex-Server answered with", "SynoClient", (contents.decode("UTF-8"),))
    except urllib.error.URLError:
        errmsg("Server is not started yet, start the Triggered Task with the right mode"); exit()
