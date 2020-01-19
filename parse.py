import os, re
from collections import namedtuple
from configparser import ConfigParser
from prints import errmsg

config_types = ["vs-handbrake", "vs-synoindex"]

def enum(enum):
    return enum.replace(" ", "").split(",")

def get_docker_ip(scope):
    ''' Get the docker0 IP address with or without external packages. '''

    if scope == "host":
        import netifaces as ni
        ni.ifaddresses('docker0')
        ip = ni.ifaddresses('docker0')[ni.AF_INET][0]['addr']
    else:
        import subprocess
        ps = subprocess.Popen(('ip', 'route', 'show'), stdout=subprocess.PIPE)
        output = subprocess.check_output(('grep', 'default'), stdin=ps.stdout)
        ps.wait()
        ip = re.search(r'([0-9]{1,3}[\.]){3}[0-9]{1,3}', output.decode('utf-8'), flags=0).group()
    return ip

def parse_docker_mappings():

    ## Get all mounts of the docker container
    import subprocess
    ps = subprocess.Popen(('mount'), stdout=subprocess.PIPE)
    output = subprocess.check_output(('grep', '^/dev/'), stdin=ps.stdout)
    ps.wait()

    ## Parse the output of the mount command
    mounts = [l for l in output.decode().split("\n") if len(l) > 0]
    mounts = [m for m in mounts if "/etc/" not in m.split(" ")[2] and m.split(" ")[2] != "/"]
    mounts = [m for m in mounts if "@docker" not in m]
    mounts = [(m.split()[2], m.split(",")[-1][:-1]) for m in mounts]
    mounts = [(m[0], m[1].split("=")[-1]) for m in mounts]
    mounts = [(m[0], m[1].replace("@syno", "volume1")) for m in mounts]

    return mounts

def parse_cfg_transmission(scope, codecs):

    ## Check the scope
    if (scope != "docker"):
        errmsg("Transmission should always run inside docker container")
        exit()

    ## Create config Namespace
    fields=["mapping", "handbrake", "codecs"]
    cfg = namedtuple('cfg', " ".join(fields))
    cfg.__new__.__defaults__ = (None,) * len(cfg._fields)

    ## Get all transmission related configs
    mapping = parse_docker_mappings()
    handbrake = [m[0] for m in mapping if "handbrake" in m[0]]
    handbrake = handbrake[0] if (len(handbrake) > 0) else None

    return cfg(mapping, handbrake, codecs)

def parse_cfg_handbrake(config, sections, fields, scope):

    ## Get the different episode and movie paths
    handbrake_movies = enum(config.get(sections[0], fields[0]))
    handbrake_series = enum(config.get(sections[0], fields[1]))

    return (handbrake_movies, handbrake_series)

def parse_cfg_synoindex(config, sections, fields, scope):

    ## Get all server configurations from config file
    ip = get_docker_ip(scope)
    port = int(config.get(sections[0], 'server_port'))
    url = "http://%s:%s" % (ip, port)

    ## Get the debug files
    server_logs = config.get(sections[0], fields[3])
    client_logs = config.get(sections[1], fields[4])

    return (ip, port, url, server_logs, client_logs)

def parse_dockerpath(mapping, filepath):
    """ Convert a path within docker container to hostsystem path. """

    ## General validation
    if not any(m[0] in filepath for m in mapping):
        return -1

    ## Replace the docker path to the host path
    for m in mapping:
            file_tmp = filepath.replace(m[0], m[1])
            if file_tmp != filepath:
                (source_host, root_host) = (file_tmp, m[1])
    return (source_host, root_host)

def parse_cfg(config_file, config_type, scope):
    ''' Parse all configuration options of the config file. '''

    ## Check whether the config type is supported
    if config_type not in config_types:
        exit("Error: Config type is not supported: %s" % (config_type))

    ## Read the config file
    config = ConfigParser()
    config.read(config_file)

    ## VS-Handbrake
    if (config_type == "vs-handbrake"):
        sections = ['Handbrake']
        fields = ["handbrake_movies", "handbrake_series"]

    ## VS-SynoIndex
    elif (config_type == "vs-synoindex"):
        sections = ["Server", "Client"]
        fields = ["port", "ip", "url", "server_logs", "client_logs"]

    ## Check whether all sections are present and initialize config Namespace
    _ = [exit('Error: Section (%s) missing' % s) for s in sections if not config.has_section(s)]
    cfg = namedtuple('cfg', " ".join(fields))
    cfg.__new__.__defaults__ = (None,) * len(cfg._fields)

    if (config_type == "vs-handbrake"):
        (handbrake_movies, handbrake_series) = parse_cfg_handbrake(config, sections, fields, scope)
        parsed_cfg = cfg(handbrake_movies, handbrake_series)

    if (config_type == "vs-synoindex"):
        (ip, port, url, server_logs, client_logs) = parse_cfg_synoindex(config, sections, fields, scope)
        parsed_cfg = cfg(port, ip, url, server_logs, client_logs)

    return parsed_cfg