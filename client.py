#################################################
##           Scope: Docker-Container           ##
#################################################
import os, re, urllib
from urllib.request import urlopen
from urllib.parse import urlencode

## Add the VS-Utils submodule to the python path
from prints import debugmsg, errmsg
from parse import get_docker_ip

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
def client(source_host, port, output_host=None, scope="docker"):

    ## Get the URL to the Syno-Index server
    url = client_get_url(scope, port)

    ## Call the url and get the answer of the server
    if not output_host:
        query_vars = {'source_host': source_host}
    else:
        query_vars = {'source_host': source_host, 'output_host': output_host}
    url = url + urlencode(query_vars)
    debugmsg("Sent to SynoIndex-Server", "SynoClient")
    contents = urlopen(url).read()
    debugmsg("SynoIndex-Server answered with", "SynoClient", (contents,))