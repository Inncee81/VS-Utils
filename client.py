import os, re, urllib
from urllib.request import urlopen
from urllib.parse import urlencode
from prints import debugmsg, errmsg

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

    url = "http://{ip}:{port}/synoindex?".format(ip=ip, port=port)
    return url

### Synoindex-Client
def client(source_host, port, output_host="", original="0", scope="docker"):

    ## Get the URL to the Syno-Index server
    url = client_get_url(scope, port)

    ## Call the url and get the answer of the server
    query_vars = {"source_host": source_host, "output_host": output_host,
                  "original": original}

    url = url + urlencode(query_vars)
    debugmsg("Send arguments to SynoIndex-Server", "SynoClient", (source_host, port, output_host, original))
    contents = urlopen(url).read()
    debugmsg("SynoIndex-Server answered with", "SynoClient", (contents,))
